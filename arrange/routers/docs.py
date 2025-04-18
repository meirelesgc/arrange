from fastapi import APIRouter, Depends

from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.services import doc_service

router = APIRouter()


@router.get('/docs/')
async def list_docs(conn: Connection = Depends(get_conn)):
    return await doc_service.list_docs(conn)
