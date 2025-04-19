from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import user_models


async def post_user(conn: Connection, user: user_models.User):
    params = user.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.users (id, username, email, password, created_at)
        VALUES (%(id)s, %(username)s, %(email)s, %(password)s, %(created_at)s);
        """
    return await conn.exec(SCRIPT_SQL, params)


async def get_user(conn: Connection, id: UUID):
    one = False
    params = {}

    if id:
        one = True
        params['id'] = id

    SCRIPT_SQL = """
        SELECT id, username, email, password, created_at, updated_at
        FROM public.users;
        """
    return await conn.select(SCRIPT_SQL, params, one)
