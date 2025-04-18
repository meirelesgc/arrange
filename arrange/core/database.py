from arrange.config import Settings
from arrange.core.connection import Connection

conn = Connection(Settings().get_connection_string(), max_size=20, timeout=10)


async def get_conn():
    yield conn
