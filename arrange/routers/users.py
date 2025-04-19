from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.models import user_models
from arrange.services import user_service

router = APIRouter()


@router.post(
    '/user/',
    status_code=HTTPStatus.CREATED,
    response_model=user_models.User,
)
async def post_user(
    user: user_models.CreateUser,
    conn: Connection = Depends(get_conn),
):
    return await user_service.post_user(conn, user)


@router.get(
    '/user/',
    status_code=HTTPStatus.OK,
    response_model=list[user_models.User],
)
async def get_user(conn: Connection = Depends(get_conn)):
    return await user_service.get_user(conn)


@router.get(
    '/user/{id}/',
    status_code=HTTPStatus.OK,
    response_model=user_models.User,
)
async def get_single_user(id: UUID, conn: Connection = Depends(get_conn)):
    return await user_service.get_user(conn, id)
