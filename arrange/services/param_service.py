from datetime import datetime
from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import param_models
from arrange.repositories import param_repository


async def post_param(
    conn: Connection,
    param: param_models.CreateParam,
    current_user,
):
    param = param_models.Param(**param.model_dump())
    await param_repository.post_param(conn, param, current_user)
    return param


async def get_param(conn: Connection):
    return await param_repository.get_param(conn)


async def put_param(conn: Connection, param: param_models.Param):
    param.updated_at = datetime.now()
    await param_repository.put_param(conn, param)
    return param


async def delete_param(conn: Connection, id: UUID):
    await param_repository.delete_param(conn, id)
