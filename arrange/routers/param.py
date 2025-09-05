from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.models import param_models, user_models
from arrange.security import get_current_user
from arrange.services import param_service

router = APIRouter()


@router.post(
    '/param/',
    status_code=HTTPStatus.CREATED,
    response_model=param_models.Param,
)
async def post_param(
    param: param_models.CreateParam,
    conn: Connection = Depends(get_conn),
    current_user: user_models.User = Depends(get_current_user),
):
    return await param_service.post_param(conn, param, current_user)


@router.get(
    '/param/',
    status_code=HTTPStatus.OK,
    response_model=list[param_models.Param],
)
async def get_param(conn: Connection = Depends(get_conn)):
    return await param_service.get_param(conn)


@router.put(
    '/param/',
    status_code=HTTPStatus.OK,
    response_model=param_models.Param,
)
async def put_param(
    param: param_models.Param,
    conn: Connection = Depends(get_conn),
):
    return await param_service.put_param(conn, param)


@router.delete('/param/{id}/', status_code=HTTPStatus.NO_CONTENT)
async def delete_param(id: UUID, conn: Connection = Depends(get_conn)):
    return await param_service.delete_param(conn, id)
