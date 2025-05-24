from collections import defaultdict
from pathlib import Path
from uuid import UUID

import spacy
from fastapi import HTTPException, UploadFile
from langchain.schema import Document
from langchain.schema.document import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader

from arrange.core.connection import Connection
from arrange.models import doc_models
from arrange.repositories import arrange_repository, doc_repository

nlp = spacy.load('pt_core_news_lg')


async def get_doc(conn: Connection):
    result = await doc_repository.get_doc(conn)
    return result


def load_documents(doc: doc_models.Doc):
    loader = PyMuPDFLoader(f'storage/{doc.id}.pdf')
    chunks = list(loader.lazy_load())
    docs = [chunk for chunk in chunks if chunk.page_content]

    if not docs:
        loader = UnstructuredLoader(
            file_path=f'storage/{doc.id}.pdf',
            strategy='hi_res',
            languages=['por'],
        )
        chunks = [chunk for chunk in loader.lazy_load() if chunk.page_content]

        pages = defaultdict(list)
        for chunk in chunks:
            page_number = chunk.metadata.get('page_number')
            if page_number is not None:
                pages[page_number].append(chunk)

        docs = []
        for page_number, page_chunks in pages.items():
            content = [chunk.page_content for chunk in page_chunks]
            content = '\n'.join(content)
            merged_metadata = page_chunks[0].metadata.copy()
            document = Document(page_content=content, metadata=merged_metadata)
            docs.append(document)
    for chunk in docs:
        print(chunk)
        print('\n\n---\n\n')
    return docs


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=600,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def index_chunks(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get('source')
        page = chunk.metadata.get('page')
        current_page_id = f'{source}:{page}'

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f'{current_page_id}:{current_chunk_index}'
        last_page_id = current_page_id

        chunk.metadata['id'] = chunk_id

    return chunks


async def add_doc_vectorstore(vectorstore: VectorStore, doc: doc_models.Doc):
    chunks = load_documents(doc)
    # chunks = split_documents(chunks)
    # chunks = index_chunks(chunks)
    chunks = [chunk for chunk in chunks if chunk.page_content]
    await vectorstore.aadd_documents(chunks)


async def post_doc(
    conn: Connection, vectorstore: VectorStore, file: UploadFile
):
    doc = doc_models.Doc(name=file.filename)
    with open(f'storage/{doc.id}.pdf', 'wb') as buffer:
        buffer.write(file.file.read())
    # --- INSERT
    await add_doc_vectorstore(vectorstore, doc)
    await doc_repository.post_doc(conn, doc)
    await arrange_repository.post_doc(conn, doc.id)
    # ---
    return doc


async def delete_doc(conn: Connection, id: UUID):
    path = Path(f'storage/{id}.pdf')
    if not path.exists():
        raise HTTPException(status_code=404, detail='File not found')
    path.unlink()
    await doc_repository.delete_doc(conn, id)
