from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import doc_models


async def post_doc(conn: Connection, doc: doc_models.Doc):
    params = doc.model_dump()

    SCRIPT_SQL = """
        INSERT INTO public.docs(id, name, created_at)
        VALUES (%(id)s, %(name)s, %(created_at)s);
        """

    await conn.exec(SCRIPT_SQL, params)


async def get_doc(conn: Connection):
    SCRIPT_SQL = """
        SELECT id, name, created_at, updated_at
        FROM docs;
        """
    return await conn.select(SCRIPT_SQL)


async def delete_doc(conn: Connection, id: UUID):
    params = {'id': id}
    SCRIPT_SQL = 'DELETE FROM public.docs WHERE id = %(id)s;'
    await conn.exec(SCRIPT_SQL, params)
