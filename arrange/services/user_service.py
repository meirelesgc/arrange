from arrange.core.connection import Connection
from arrange.models import user_models
from arrange.repositories import user_repository


async def post_user(user: user_models.CreateUser, conn: Connection):
    user = user_models.User(**user.model_dump())
    await user_repository.post_user(user, conn)
    return user


async def get_user(conn: Connection):
    users = await user_repository.get_user(conn)
    return users
