import json
from http import HTTPStatus
from time import time
from typing import Literal, Optional
from uuid import UUID

from fastapi import HTTPException
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, Field, create_model

from arrange.core.connection import Connection
from arrange.models import arrange_models, param_models
from arrange.repositories import arrange_repository, param_repository


async def get_chunks(vectorstore: VectorStore, id: UUID, query: str):
    filter_source = {'source': {'$eq': f'storage/{id}.pdf'}}
    return await vectorstore.asimilarity_search(
        query, k=5, filter=filter_source
    )


def build_details_chain(local_model: BaseChatModel):
    template = """
    {content}

    Estou avaliando suas capacidades. Com base no conteúdo fictício acima.
    Ajude-me a estruturar um JSON contendo os metadados do arquivo.

    {format_instructions}

    {query}
    """  # noqa: E501

    parser = PydanticOutputParser(
        pydantic_object=arrange_models.ArrangeDetails
    )
    prompt = PromptTemplate(
        template=template,
        input_variables=['content', 'query'],
        partial_variables={
            'format_instructions': parser.get_format_instructions()
        },
    )
    return prompt | local_model | parser


async def arrange_doc_details(
    conn: Connection,
    vectorstore: VectorStore,
    local_model: BaseChatModel,
    id: UUID,
):
    start_time = time()
    chunks = await get_chunks(
        vectorstore, id, 'Hospital, Endereço, Data, Telefone, CNPj'
    )
    chain = build_details_chain(local_model)
    query = 'Responda apropriadamente, seguindo o formato orientado'
    content = '\n\n---\n\n'.join([chunk.page_content for chunk in chunks])
    output = chain.invoke({'content': content, 'query': query})
    duration = time() - start_time
    await arrange_repository.arrange_doc(
        conn, id, output.model_dump_json(), 'DETAILS', duration
    )
    return output


def build_patient_chain(local_model: BaseChatModel):
    template = """
        {content}

        Estou avaliando suas capacidades. Com base no conteúdo fictício acima.
        Ajude-me a estruturar um JSON contendo os metadados do arquivo.

        {format_instructions}

        {query}
        """  # noqa: E501

    parser = PydanticOutputParser(
        pydantic_object=arrange_models.ArrangePatient
    )
    prompt = PromptTemplate(
        template=template,
        input_variables=['content', 'query'],
        partial_variables={
            'format_instructions': parser.get_format_instructions()
        },
    )
    return prompt | local_model | parser


async def arrange_doc_patient(
    conn: Connection,
    vectorstore: VectorStore,
    local_model: BaseChatModel,
    id: UUID,
):
    start_time = time()
    chunks = await get_chunks(
        vectorstore,
        id,
        'Hospital, endereço completo, data de emissão, telefone de contato',
    )
    chain = build_patient_chain(local_model)
    query = 'Responda apropriadamente, seguindo o formato orientado'
    content = '\n\n---\n\n'.join([chunk.page_content for chunk in chunks])
    output = chain.invoke({'content': content, 'query': query})
    duration = time() - start_time
    await arrange_repository.arrange_doc(
        conn, id, output.model_dump_json(), 'PATIENTS', duration
    )
    return output


async def get_chunks_by_params(
    vectorstore: VectorStore,
    params: list[param_models.Param],
    id: UUID,
):
    chunks = {}
    for param in params:
        query = ', '.join(param.get('synonyms') + [param.get('name')])
        raw_chunks = await get_chunks(vectorstore, id, query)
        for chunk in raw_chunks:
            chunk_id = chunk.metadata.get('id')
            if chunk_id not in chunks:
                chunks[chunk_id] = {'chunk': chunk, 'params': []}
            chunks[chunk_id]['params'].append(param)
    return chunks


def dynamic_model(
    params: list[param_models.Param],
    model_name: str = 'Metrics',
    docstring: str = 'Dados que devem ser extraidos do conteudo.',
) -> type[BaseModel]:
    field_definitions: dict[str, str] = {}
    for param in params:
        name = param['name'].strip().lower().replace(' ', '_')
        description = f'Sinônimos: {", ".join(param["synonyms"])}'
        field_definitions[name] = (
            Optional[str],
            Field(None, description=description),
        )
    return create_model(model_name, __doc__=docstring, **field_definitions)


def build_metrics_chain(
    local_model: BaseChatModel,
    params: list[param_models.Param],
):
    template = """
        {content}

        Estou avaliando suas capacidades. Com base no conteúdo fictício acima, siga as orientações e ajude-me a realizara estruturar um JSON contendo os dados do arquivo, quero um json simples.

        {format_instructions}

        {query}
        """  # noqa: E501

    parser = PydanticOutputParser(pydantic_object=dynamic_model(params))
    prompt = PromptTemplate(
        template=template,
        input_variables=['content', 'query'],
        partial_variables={
            'format_instructions': parser.get_format_instructions()
        },
    )
    return prompt | local_model | parser


async def arrange_doc_metrics(
    conn: Connection,
    vectorstore: VectorStore,
    local_model: BaseChatModel,
    id: UUID,
):
    start_time = time()
    params = await param_repository.get_param(conn)
    if not params:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Required parameters not found.',
        )
    chunks = await get_chunks_by_params(vectorstore, params, id)

    aggregated_output = {}
    for chunk in chunks.values():
        chain = build_metrics_chain(local_model, chunk['params'])
        query = 'Responda apropriadamente, seguindo o formato orientado'
        content = chunk['chunk'].page_content
        output = chain.invoke({'content': content, 'query': query})
        for field, value in output.model_dump().items():
            if field not in aggregated_output:
                aggregated_output[field] = set()
            aggregated_output[field].add(value)
    aggregated_output = {
        field: list(values) for field, values in aggregated_output.items()
    }
    output = json.dumps(aggregated_output)
    duration = time() - start_time
    await arrange_repository.arrange_doc(conn, id, output, 'DETAILS', duration)
    return aggregated_output


async def get_arrange(
    conn: Connection, id: UUID, type: Literal['DETAILS', 'PATIENTS', 'METRICS']
):
    return await arrange_repository.get_arrange_metrics(conn, id, type)
