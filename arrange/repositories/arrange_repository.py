import json
from datetime import datetime
from typing import Literal
from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import arrange_models


async def export_arranges(conn: Connection):
    SCRIPT_SQL = """
        SELECT d.id, d.name, a.output, a.type
        FROM docs d
        LEFT JOIN arranges a
            ON a.doc_id = d.id
        WHERE a.status = 'DONE'
        """
    return await conn.select(SCRIPT_SQL, {}, one=False)


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
    params = arrange.model_dump(mode='json')
    params['output'] = json.dumps(params['output'])

    SCRIPT_SQL = """
        UPDATE public.arranges SET output = %(output)s, status = %(status)s,
            duration = %(duration)s, updated_at = %(updated_at)s
        WHERE doc_id = %(doc_id)s AND type = %(type)s;
        """
    await conn.exec(SCRIPT_SQL, params)

    SCRIPT_SQL = """
        INSERT INTO logs.arranges(id, doc_id, output, type, duration,
            created_at)
        VALUES (%(id)s, %(doc_id)s, %(output)s, %(type)s, %(duration)s,
            %(created_at)s);
        """
    await conn.exec(SCRIPT_SQL, params)


async def patch_arrange(
    id: UUID,
    output: dict,
    type: Literal['DETAILS', 'PATIENTS', 'METRICS'],
    conn: Connection,
):
    params = {
        'id': id,
        'output': json.dumps(output),
        'updated_at': datetime.now(),
        'type': type,
    }

    SCRIPT_SQL = """
        UPDATE public.arranges SET output = %(output)s, status = 'DONE',
            updated_at = %(updated_at)s
        WHERE doc_id = %(id)s AND type = %(type)s;
        """
    await conn.exec(SCRIPT_SQL, params)


async def match_patient(
    conn: Connection,
    output: arrange_models.ArrangePatient,
):
    params = output.model_dump(mode='json')
    SCRIPT_SQL = """
        SELECT id,
            COALESCE(similarity(full_name, %(full_name)s), 0) * 2 +
            CASE
                WHEN date_of_birth = %(date_of_birth)s THEN 1
                ELSE 0
            END +
            CASE
                WHEN gender = %(gender)s THEN 0.5
                ELSE 0
            END +
            CASE
                WHEN date_of_birth = %(date_of_birth)s AND gender = %(gender)s THEN 1
                ELSE 0
            END +
            CASE
                WHEN phone IS NOT NULL AND phone = %(phone)s THEN 1
                ELSE 0
            END +
            CASE
                WHEN LOWER(email) = LOWER(%(email)s) THEN 1
                ELSE COALESCE(similarity(email, %(email)s), 0)
            END AS similarity
        FROM public.patients
        ORDER BY similarity DESC
    """  # noqa: E501
    result = await conn.select(SCRIPT_SQL, params, one=True)
    FILTER = 3

    if result and result.get('similarity', 0) >= FILTER:
        SCRIPT_SQL = """
            UPDATE public.patients
            SET full_name = COALESCE(full_name, %(full_name)s),
                gender = COALESCE(gender, %(gender)s),
                phone = COALESCE(phone, %(phone)s),
                email = COALESCE(email, %(email)s),
                date_of_birth = COALESCE(date_of_birth, %(date_of_birth)s),
                updated_at = NOW()
            WHERE id = %(id)s;
        """
        params = output.model_dump(mode='json')
        params['id'] = result.get('id')
        return await conn.exec(SCRIPT_SQL, params)
    SCRIPT_SQL = """
        INSERT INTO public.patients(full_name, gender, phone, email, date_of_birth)
        VALUES (%(full_name)s, %(gender)s, %(phone)s, %(email)s, %(date_of_birth)s);
    """  # noqa: E501
    return await conn.exec(SCRIPT_SQL, params)
