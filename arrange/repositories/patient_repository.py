from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import patient_models


async def get_patient(conn: Connection):
    SCRIPT_SQL = """
        SELECT id, full_name, gender, phone, email, date_of_birth,
               created_at, updated_at
        FROM public.patients;
        """
    return await conn.select(SCRIPT_SQL)


async def post_patient(conn: Connection, patient: patient_models.Patient):
    params = patient.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.patients (id, full_name, gender, phone, email,
            date_of_birth, created_at)
        VALUES (%(id)s, %(full_name)s, %(gender)s, %(phone)s, %(email)s,
            %(date_of_birth)s, %(created_at)s);
        """
    await conn.exec(SCRIPT_SQL, params)


async def put_patient(conn: Connection, patient: patient_models.Patient):
    params = patient.model_dump()
    SCRIPT_SQL = """
        UPDATE public.patients
        SET full_name = %(full_name)s,
            gender = %(gender)s,
            phone = %(phone)s,
            email = %(email)s,
            date_of_birth = %(date_of_birth)s,
            updated_at = %(updated_at)s
        WHERE id = %(id)s;
        """
    await conn.exec(SCRIPT_SQL, params)


async def delete_patient(conn: Connection, id: UUID):
    SCRIPT_SQL = """
        DELETE FROM public.patients
        WHERE id = %(id)s;
        """
    await conn.exec(SCRIPT_SQL, {'id': id})
