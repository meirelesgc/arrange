from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.models import patient_models
from arrange.services import patient_service

router = APIRouter()


@router.get(
    '/patient/',
    status_code=HTTPStatus.OK,
    response_model=list[patient_models.Patient],
)
async def get_patient(conn: Connection = Depends(get_conn)):
    return await patient_service.get_patient(conn)


@router.post(
    '/patient/',
    status_code=HTTPStatus.OK,
    response_model=patient_models.Patient,
)
async def post_patient(
    patient: patient_models.CreatePatient,
    conn: Connection = Depends(get_conn),
):
    return await patient_service.post_patient(conn, patient)


@router.put(
    '/patient/',
    status_code=HTTPStatus.OK,
    response_model=patient_models.Patient,
)
async def put_patient(
    patient: patient_models.Patient,
    conn: Connection = Depends(get_conn),
):
    return await patient_service.put_patient(conn, patient)


@router.delete(
    '/patient/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_patient(
    id: UUID,
    conn: Connection = Depends(get_conn),
):
    return await patient_service.delete_patient(conn, id)
