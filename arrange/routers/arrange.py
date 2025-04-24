from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStore

from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.core.model import get_local_model
from arrange.core.vectorstore import get_vectorstore
from arrange.services import arrange_service

router = APIRouter()


@router.post('/arrange/{id}/metrics/', status_code=HTTPStatus.OK)
async def arrange_doc_metrics(
    id: UUID,
    conn: Connection = Depends(get_conn),
    vectorstore: VectorStore = Depends(get_vectorstore),
    local_model: BaseChatModel = Depends(get_local_model),
):
    return await arrange_service.arrange_doc_metrics(
        conn, vectorstore, local_model, id
    )


@router.post('/arrange/{id}/details/', status_code=HTTPStatus.OK)
async def arrange_doc_details(
    id: UUID,
    conn: Connection = Depends(get_conn),
    vectorstore: VectorStore = Depends(get_vectorstore),
    local_model: BaseChatModel = Depends(get_local_model),
):
    return await arrange_service.arrange_doc_details(
        conn, vectorstore, local_model, id
    )


@router.post('/arrange/{id}/patient/', status_code=HTTPStatus.OK)
async def arrange_doc_patient(
    id: UUID,
    conn: Connection = Depends(get_conn),
    vectorstore: VectorStore = Depends(get_vectorstore),
    local_model: BaseChatModel = Depends(get_local_model),
):
    return await arrange_service.arrange_doc_patient(
        conn, vectorstore, local_model, id
    )
