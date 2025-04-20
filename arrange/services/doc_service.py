from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile
from langchain.schema.document import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from arrange.core.connection import Connection
from arrange.models import doc_models
from arrange.repositories import doc_repository


async def get_doc(conn: Connection):
    result = await doc_repository.get_doc(conn)
    return result


def load_documents(doc: doc_models.Doc):
    document_loader = PyPDFLoader(f'storage/{doc.id}.pdf')
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=8000,
        chunk_overlap=800,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


async def add_doc_vectorstore(vectorstore: VectorStore, doc: doc_models.Doc):
    chunks = load_documents(doc)
    chunks = split_documents(chunks)
    await vectorstore.aadd_documents(chunks)


async def post_doc(
    conn: Connection, vectorstore: VectorStore, file: UploadFile
):
    doc = doc_models.Doc(name=file.filename)
    with open(f'storage/{doc.id}.pdf', 'wb') as buffer:
        buffer.write(file.file.read())
    await add_doc_vectorstore(vectorstore, doc)
    await doc_repository.post_doc(conn, doc)
    return doc


async def delete_doc(conn: Connection, id: UUID):
    path = Path(f'storage/{id}.pdf')
    if not path.exists():
        raise HTTPException(status_code=404, detail='File not found')
    path.unlink()
    await doc_repository.delete_doc(conn, id)
