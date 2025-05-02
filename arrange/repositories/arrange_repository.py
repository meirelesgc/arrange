import json
from typing import Literal
from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import arrange_models


async def get_arrange_metrics(
    conn: Connection, id: UUID, type: Literal['DETAILS', 'PATIENTS', 'METRICS']
):
    one = True
    params = {'id': id, 'type': type}
    SCRIPT_SQL = """
        SELECT doc_id, output, status, type, duration, updated_at
        FROM public.arranges
        WHERE 1 = 1
            AND type = %(type)s
            AND doc_id = %(id)s;
        """
    return await conn.select(SCRIPT_SQL, params, one)


async def post_doc(conn: Connection, id: UUID):
    for type in ['DETAILS', 'PATIENTS', 'METRICS']:
        params = {'id': id, 'type': type}
        SCRIPT_SQL = """
            INSERT INTO public.arranges(doc_id, type)
            VALUES (%(id)s, %(type)s);
            """
        await conn.exec(SCRIPT_SQL, params)


async def arrange_doc(conn: Connection, arrange: arrange_models.Arrange):
    params = arrange.model_dump()
    params['output'] = json.dumps(params['output'])

    SCRIPT_SQL = """
        UPDATE public.arranges SET output = %(output)s, status = %(status)s,
            duration = %(duration)s, updated_at = %(updated_at)s
        WHERE doc_id = %(doc_id)s;
        """
    await conn.exec(SCRIPT_SQL, params)

    SCRIPT_SQL = """
        INSERT INTO logs.arranges(id, doc_id, output, type, duration,
            created_at)
        VALUES (%(id)s, %(doc_id)s, %(output)s, %(type)s, %(duration)s,
            %(created_at)s);
        """
    await conn.exec(SCRIPT_SQL, params)
