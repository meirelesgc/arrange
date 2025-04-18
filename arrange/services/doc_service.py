from arrange.core.connection import Connection
from arrange.repositories import doc_repository


async def list_docs(conn: Connection):
    result = await doc_repository.list_docs(conn)
    return result
