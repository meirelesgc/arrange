from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStore

from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.core.model import get_local_model, get_model
from arrange.core.vectorstore import get_vectorstore
from arrange.models import arrange_models, patient_models
from arrange.services import arrange_service

router = APIRouter()


@router.put(
    '/arrange/{id}/metrics/',
    status_code=HTTPStatus.OK,
    response_model=arrange_models.Arrange,
)
async def put_arrange_metrics(
    id: UUID,
    conn: Connection = Depends(get_conn),
    vectorstore: VectorStore = Depends(get_vectorstore),
    model: BaseChatModel = Depends(get_model),
):
    return await arrange_service.put_arrange_metrics(
        conn, vectorstore, model, id
    )


@router.patch('/arrange/{id}/metrics/', status_code=HTTPStatus.OK)
async def patch_arrange_metrics(
    id: UUID, output: dict, conn: Connection = Depends(get_conn)
):
    return await arrange_service.patch_arrange(id, output, 'METRICS', conn)


@router.get(
    '/arrange/{id}/metrics/',
    status_code=HTTPStatus.OK,
    response_model=arrange_models.Arrange,
)
async def get_arrange_metrics(id: UUID, conn: Connection = Depends(get_conn)):
    return await arrange_service.get_arrange(conn, id, 'METRICS')


@router.put(
    '/arrange/{id}/details/',
    status_code=HTTPStatus.OK,
    response_model=arrange_models.Arrange,
)
async def put__details(
    id: UUID,
    conn: Connection = Depends(get_conn),
    vectorstore: VectorStore = Depends(get_vectorstore),
    local_model: BaseChatModel = Depends(get_local_model),
):
    return await arrange_service.put_arrange_details(
        conn, vectorstore, local_model, id
    )


@router.get(
    '/arrange/{id}/details/',
    status_code=HTTPStatus.OK,
    response_model=arrange_models.Arrange,
)
async def get_arrange_details(id: UUID, conn: Connection = Depends(get_conn)):
    return await arrange_service.get_arrange(conn, id, 'DETAILS')


@router.patch('/arrange/{id}/details/', status_code=HTTPStatus.OK)
async def patch_details(
    id: UUID, output: dict, conn: Connection = Depends(get_conn)
):
    return await arrange_service.patch_arrange(id, output, 'DETAILS', conn)


@router.put(
    '/arrange/{id}/patient/',
    status_code=HTTPStatus.OK,
    response_model=arrange_models.Arrange,
)
async def put_arrange_patient(
    id: UUID,
    conn: Connection = Depends(get_conn),
    vectorstore: VectorStore = Depends(get_vectorstore),
    local_model: BaseChatModel = Depends(get_local_model),
):
    return await arrange_service.put_arrange_patient(
        conn, vectorstore, local_model, id
    )


@router.get(
    '/arrange/{id}/patient/',
    status_code=HTTPStatus.OK,
    response_model=arrange_models.Arrange,
)
async def get_arrange_patient(id: UUID, conn: Connection = Depends(get_conn)):
    return await arrange_service.get_arrange(conn, id, 'PATIENTS')


@router.patch('/arrange/{id}/patient/', status_code=HTTPStatus.OK)
async def patch_patient(
    id: UUID, output: dict, conn: Connection = Depends(get_conn)
):
    return await arrange_service.patch_arrange(id, output, 'PATIENTS', conn)


@router.get('/arrange/export/', status_code=HTTPStatus.OK)
async def export_arranges(
    patients: list[patient_models.Patient],
    conn: Connection = Depends(get_conn),
):
    await arrange_service.export_arranges(conn, patients)
    file_path = 'storage/export.zip'
    return FileResponse(
        path=file_path,
        media_type='application/zip',
        headers={'Content-Disposition': 'attachment; filename="export.zip"'},
    )
