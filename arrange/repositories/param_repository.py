from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import param_models


async def post_param(
    conn: Connection,
    param: param_models.Param,
    current_user,
):
    params = param.model_dump()
    params['created_by'] = current_user.id
    SCRIPT_SQL = """
        INSERT INTO public.params (id, name, synonyms, created_by, created_at)
        VALUES (%(id)s, %(name)s, %(synonyms)s, %(created_by)s, %(created_at)s);
        """
    await conn.exec(SCRIPT_SQL, params)


async def get_param(conn: Connection):
    SCRIPT_SQL = """
        SELECT id, name, synonyms, created_at, updated_at
        FROM public.params;
        """
    return await conn.select(SCRIPT_SQL)


async def put_param(conn: Connection, param: param_models.Param):
    params = param.model_dump()
    SCRIPT_SQL = """
        UPDATE public.params
        SET name = %(name)s,
            synonyms = %(synonyms)s
        WHERE id = %(id)s;
        """
    await conn.exec(SCRIPT_SQL, params)


async def delete_param(conn: Connection, id: UUID):
    params = {'id': id}
    SCRIPT_SQL = """
        DELETE FROM public.params
        WHERE id = %(id)s;
        """
    await conn.exec(SCRIPT_SQL, params)
