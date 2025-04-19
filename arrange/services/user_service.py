from datetime import datetime
from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import user_models
from arrange.repositories import user_repository


async def post_user(conn: Connection, user: user_models.CreateUser):
    user = user_models.User(**user.model_dump())
    await user_repository.post_user(conn, user)
    return user


async def get_user(conn: Connection, id: UUID = None):
    users = await user_repository.get_user(conn, id)
    return users


async def put_user(conn: Connection, user: user_models.User):
    user.updated_at = datetime.now()
    await user_repository.put_user(conn, user)
    return user
