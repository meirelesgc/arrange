from arrange.config import Settings
from arrange.core.connection import Connection

connection_url = Settings().get_connection_string()

conn = Connection(connection_url, max_size=20, timeout=10)


async def get_conn():
    yield conn
