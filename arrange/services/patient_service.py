from datetime import datetime
from uuid import UUID

from arrange.core.connection import Connection
from arrange.models import patient_models
from arrange.repositories import patient_repository


async def get_patient(conn: Connection):
    return await patient_repository.get_patient(conn)


async def post_patient(
    conn: Connection, patient: patient_models.CreatePatient
):
    patient = patient_models.Patient(**patient.model_dump())
    await patient_repository.post_patient(conn, patient)
    return patient


async def put_patient(conn: Connection, patient: patient_models.Patient):
    patient.updated_at = datetime.now()
    await patient_repository.put_patient(conn, patient)
    return patient


async def delete_patient(conn: Connection, id: UUID):
    return await patient_repository.delete_patient(conn, id)
