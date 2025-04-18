from arrange.core.connection import Connection


async def list_docs(conn: Connection):
    SCRIPT_SQL = """
        SELECT id, name, created_at, updated_at
        FROM docs;
        """
    return await conn.select(SCRIPT_SQL)
