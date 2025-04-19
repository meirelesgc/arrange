from arrange.core.connection import Connection
from arrange.models import user_models


async def post_user(user: user_models.User, conn: Connection):
    params = user.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.users (id, username, email, password, created_at)
        VALUES (%(id)s, %(username)s, %(email)s, %(password)s, %(created_at)s);
        """
    return await conn.exec(SCRIPT_SQL, params)


async def get_user(conn: Connection):
    SCRIPT_SQL = """
        SELECT id, username, email, password, created_at, updated_at
        FROM public.users;
        """
    return await conn.select(SCRIPT_SQL)
