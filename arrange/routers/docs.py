from http import HTTPStatus

from fastapi import APIRouter, Depends, File, UploadFile

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


@router.get('/doc/')
async def get_doc(conn: Connection = Depends(get_conn)):
    return await doc_service.get_doc(conn)
