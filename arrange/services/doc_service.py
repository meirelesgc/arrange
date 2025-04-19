from fastapi import UploadFile

from arrange.core.connection import Connection
from arrange.models import doc_models
from arrange.repositories import doc_repository


async def get_doc(conn: Connection):
    result = await doc_repository.get_doc(conn)
    return result


async def post_doc(conn: Connection, file: UploadFile):
    doc = doc_models.Doc(name=file.filename)
    await doc_repository.post_doc(conn, doc)
    return doc
