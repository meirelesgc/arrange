from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile

from arrange.core.connection import Connection
from arrange.models import doc_models
from arrange.repositories import doc_repository


async def get_doc(conn: Connection):
    result = await doc_repository.get_doc(conn)
    return result


async def post_doc(conn: Connection, file: UploadFile):
    doc = doc_models.Doc(name=file.filename)
    with open(f'storage/{doc.id}.pdf', 'wb') as buffer:
        buffer.write(file.file.read())
    await doc_repository.post_doc(conn, doc)
    return doc


async def delete_doc(conn: Connection, id: UUID):
    path = Path(f'storage/{id}.pdf')
    if not path.exists():
        raise HTTPException(status_code=404, detail='File not found')
    path.unlink()
    await doc_repository.delete_doc(conn, id)
