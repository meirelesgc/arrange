import json
from io import BytesIO
from typing import override

import pytest
import pytest_asyncio
from fastapi import UploadFile
from fastapi.testclient import TestClient
from langchain_community.embeddings import FakeEmbeddings
from langchain_core.language_models.fake_chat_models import FakeChatModel
from langchain_postgres import PGVector
from testcontainers.postgres import PostgresContainer

from arrange.app import app
from arrange.core.connection import Connection
from arrange.core.database import get_conn
from arrange.core.model import get_local_model
from arrange.core.vectorstore import get_vectorstore
from arrange.services import doc_service, param_service, user_service
from tests.factories import doc_factory, param_factory, user_factory


@pytest.fixture(scope='session', autouse=True)
def postgres():
    with PostgresContainer('pgvector/pgvector:pg17') as pg:
        yield pg


async def reset_database(conn: Connection):
    SCRIPT_SQL = """
        DROP SCHEMA IF EXISTS public CASCADE;
        DROP SCHEMA IF EXISTS logs CASCADE;
        CREATE SCHEMA public;
        """
    await conn.exec(SCRIPT_SQL)
    with open('init.sql', 'r', encoding='utf-8') as buffer:
        await conn.exec(buffer.read())


@pytest_asyncio.fixture
async def conn(postgres):
    connection_url = f'postgresql://{postgres.username}:{postgres.password}@{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}/{postgres.dbname}'
    conn = Connection(connection_url, max_size=20, timeout=10)
    await conn.connect()
    await reset_database(conn)
    yield conn
    await conn.disconnect()


@pytest_asyncio.fixture
async def vectorstore(postgres):
    connection_url = f'postgresql+psycopg://{postgres.username}:{postgres.password}@{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}/{postgres.dbname}'
    vectorstore = PGVector(
        embeddings=FakeEmbeddings(size=256),
        connection=connection_url,
        use_jsonb=True,
        async_mode=True,
    )

    yield vectorstore


@pytest_asyncio.fixture
async def model():
    class FakeModel(FakeChatModel):
        @override
        def _call(
            self, messages, stop=None, run_manager=None, **kwargs
        ) -> str:
            return json.dumps({})

    return FakeModel()


@pytest.fixture
def client(conn, vectorstore, model):
    async def get_conn_override():
        yield conn

    async def get_vectorstore_override():
        yield vectorstore

    async def get_model_override():
        yield model

    app.dependency_overrides[get_conn] = get_conn_override
    app.dependency_overrides[get_vectorstore] = get_vectorstore_override
    app.dependency_overrides[get_local_model] = get_model_override
    return TestClient(app)


@pytest.fixture
def create_user(conn):
    async def _create_user(**kwargs):
        raw_user = user_factory.CreateUserFactory(**kwargs)
        password = raw_user.password
        created_user = await user_service.post_user(
            conn, raw_user, role='DEFAULT'
        )
        created_user.password = password
        return created_user

    return _create_user


@pytest.fixture
def create_param(conn):
    async def _create_param(**kwargs):
        raw_param = param_factory.CreateParamFactory(**kwargs)
        param = await param_service.post_param(conn, raw_param)
        return param

    return _create_param


@pytest.fixture
def create_admin_user(conn):
    async def _create_admin_user(**kwargs):
        raw_user = user_factory.CreateUserFactory(**kwargs)
        password = raw_user.password
        created_user = await user_service.post_user(
            conn, raw_user, role='ADMIN'
        )
        created_user.password = password
        return created_user

    return _create_admin_user


@pytest.fixture
def create_doc(conn, vectorstore):
    async def _create_doc(filename: str = 'pdf.pdf'):
        _, file_content, content_type = doc_factory.DocFactory()
        file = UploadFile(
            filename=filename,
            file=BytesIO(file_content),
        )
        doc = await doc_service.post_doc(conn, vectorstore, file)
        return doc

    return _create_doc


@pytest.fixture
def get_token(client):
    def _get_token(user):
        data = {'username': user.email, 'password': user.password}
        response = client.post('/token/', data=data)
        return response.json()['access_token']

    return _get_token
