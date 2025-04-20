from uuid import UUID

from arrange.core.connection import Connection


async def post_metrics(conn: Connection, id: UUID): ...
