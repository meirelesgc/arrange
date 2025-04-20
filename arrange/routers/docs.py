from http import HTTPStatus
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.models import doc_models, user_models
from arrange.security import get_current_user
from arrange.services import doc_service

router = APIRouter()


@router.post(
    '/doc/',
    status_code=HTTPStatus.CREATED,
    response_model=doc_models.Doc,
)
async def post_doc(
    file: UploadFile = File(...),
    current_user: user_models.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await doc_service.post_doc(conn, file)


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
