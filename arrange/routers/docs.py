from http import HTTPStatus
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from langchain_core.vectorstores import VectorStore

from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.core.vectorstore import get_vectorstore
from arrange.models import doc_models
from arrange.services import doc_service

router = APIRouter()


@router.post(
    '/doc/',
    status_code=HTTPStatus.CREATED,
    response_model=doc_models.Doc,
)
async def post_doc(
    file: UploadFile = File(...),
    conn: Connection = Depends(get_conn),
    vectorstore: VectorStore = Depends(get_vectorstore),
):
    return await doc_service.post_doc(conn, vectorstore, file)


@router.get('/doc/', response_model=list[doc_models.Doc])
async def get_doc(conn: Connection = Depends(get_conn)):
    return await doc_service.get_doc(conn)


@router.get('/doc/{id}/file/', response_class=FileResponse)
def get_doc_file(id: UUID):
    path = Path(f'storage/{id}.pdf')
    if not path.exists():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(str(path))


@router.delete('/doc/{id}/', status_code=HTTPStatus.NO_CONTENT)
async def delete_doc(id: UUID, conn: Connection = Depends(get_conn)):
    return await doc_service.delete_doc(conn, id)
