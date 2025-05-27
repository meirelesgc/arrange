from datetime import datetime
from http import HTTPStatus
from time import time
from typing import Literal, Optional
from uuid import UUID

import pandas as pd
import spacy
from fastapi import HTTPException
from langchain.schema.document import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, Field, create_model

from arrange.core.connection import Connection
from arrange.models import arrange_models, param_models
from arrange.repositories import (
    arrange_repository,
    param_repository,
)

nlp = spacy.load('pt_core_news_lg')


async def get_chunks(vectorstore: VectorStore, id: UUID, query: str):
    filter_source = {'source': {'$eq': f'storage/{id}.pdf'}}
    return await vectorstore.asimilarity_search(
        query, k=5, filter=filter_source
    )


def build_details_chain(local_model: BaseChatModel):
    template = """
    {content}

    Estou avaliando suas capacidades. Com base no conteúdo fictício acima
    ajude-me a estruturar um JSON contendo os metadados do arquivo.

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


async def put_arrange_details(
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

    arrange = arrange_models.Arrange(
        doc_id=id,
        output=output.model_dump(),
        status='STANDBY',
        type='DETAILS',
        duration=duration,
        updated_at=datetime.now(),
    )
    await arrange_repository.arrange_doc(conn, arrange)
    return arrange


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


async def put_arrange_patient(
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
    arrange = arrange_models.Arrange(
        doc_id=id,
        output=output.model_dump(),
        status='STANDBY',
        type='PATIENTS',
        duration=duration,
        updated_at=datetime.now(),
    )
    await arrange_repository.arrange_doc(conn, arrange)
    await match_patient(conn, output)
    return arrange


async def match_patient(conn, output: arrange_models.ArrangePatient):
    await arrange_repository.match_patient(conn, output)


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


def clean_documents(doc: list[Document]):
    text = doc.page_content
    spacy_doc = nlp(text)
    spans = [ent for ent in spacy_doc.ents]
    spans = sorted(spans, key=lambda x: x.start_char, reverse=True)

    for span in spans:
        start, end = span.start_char, span.end_char
        text = text[:start] + text[end:]
    doc.page_content = text


async def put_arrange_metrics(
    conn: Connection,
    vectorstore: VectorStore,
    model: BaseChatModel,
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
        chain = build_metrics_chain(model, chunk['params'])
        query = 'Responda apropriadamente, seguindo o formato orientado'
        clean_documents(chunk['chunk'])
        content = chunk['chunk'].page_content
        output = chain.invoke({'content': content, 'query': query})
        for field, value in output.model_dump().items():
            if field not in aggregated_output:
                aggregated_output[field] = []

            if value is not None:
                aggregated_output[field].append(value)

    duration = time() - start_time
    arrange = arrange_models.Arrange(
        doc_id=id,
        output=aggregated_output,
        status='STANDBY',
        type='METRICS',
        duration=duration,
        updated_at=datetime.now(),
    )
    await arrange_repository.arrange_doc(conn, arrange)
    return arrange


async def get_arrange(
    conn: Connection, id: UUID, type: Literal['DETAILS', 'PATIENTS', 'METRICS']
):
    return await arrange_repository.get_arrange_metrics(conn, id, type)


async def patch_arrange(
    id: UUID,
    output: dict,
    type: Literal['DETAILS', 'PATIENTS', 'METRICS'],
    conn: Connection,
):
    await arrange_repository.patch_arrange(id, output, type, conn)


def normalize_dict(data: dict) -> dict:
    return {
        key: (value[0] if isinstance(value, list) and value else None)
        for key, value in data.items()
    }


async def export_arranges(conn: Connection):
    arranges = await arrange_repository.export_arranges(conn)
    if not arranges:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='No arranges found.',
        )
    arranges = pd.DataFrame(arranges)
    arranges = arranges.pivot_table(
        index=['id', 'name'],
        columns='type',
        values='output',
        aggfunc='first',
        fill_value={},
    ).reset_index()

    arranges.columns = [
        col.lower() if isinstance(col, str) else col
        for col in arranges.columns
    ]

    for col in ['metrics', 'details', 'patients']:
        if col in arranges.columns:
            arranges[col] = arranges[col].apply(normalize_dict)

    arranges.to_csv('storage/export.csv', index=False, encoding='utf-8-sig')
