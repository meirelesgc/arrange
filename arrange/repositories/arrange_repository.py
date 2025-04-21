from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from arrange.core.connection import Connection


async def arrange_doc(
    conn: Connection,
    id: UUID,
    output: BaseModel,
    type: Literal['DETAILS', 'PATIENTS', 'METRICS'],
    duration: float,
):
    params = {
        'id': id,
        'output': output,
        'status': 'DONE',
        'duration': duration,
        'type': type,
        'updated_at': datetime.now(),
    }
    SCRIPT_SQL = """
        UPDATE public.arranges SET output = %(output)s, status = %(status)s,
            duration = %(duration)s, updated_at = %(updated_at)s
        WHERE doc_id = %(id)s;
        """
    await conn.exec(SCRIPT_SQL, params)
