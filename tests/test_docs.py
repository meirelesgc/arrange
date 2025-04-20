from http import HTTPStatus
from pathlib import Path
from uuid import uuid4

import pytest

from tests.factories import doc_factory


@pytest.mark.asyncio
async def test_post_doc(client, create_user, get_token):
    user = await create_user()
    token = get_token(user)
    file = {'file': doc_factory.DocFactory()}

    response = client.post(
        '/doc/',
        headers={'Authorization': f'Bearer {token}'},
        files=file,
    )

    assert response.status_code == HTTPStatus.CREATED
    path = Path(f'storage/{response.json()["id"]}.pdf')
    assert path.exists()
    path.unlink()


def test_get_doc(client):
    LENGTH = 0
    response = client.get('/doc/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_one_doc(client, create_doc):
    LENGTH = 1

    for _ in range(0, LENGTH):
        await create_doc()

    response = client.get('/doc/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_two_docs(client, create_doc):
    LENGTH = 2

    for _ in range(0, LENGTH):
        await create_doc(filename=f'{_}')

    response = client.get('/doc/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_doc_file(client, create_doc):
    doc = await create_doc()

    response = client.get(f'/doc/{doc.id}/file/')
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_doc_file_not_found(client):
    response = client.get(f'/doc/{uuid4()}/file/')
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_doc(client, create_doc):
    LENGTH = 2

    for _ in range(0, LENGTH):
        doc = await create_doc(filename=f'{_}')

    response = client.delete(f'/doc/{doc.id}/')
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get('/doc/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH - 1


@pytest.mark.asyncio
async def test_delete_doc_file_not_found(client):
    response = client.delete(f'/doc/{uuid4()}/')
    assert response.status_code == HTTPStatus.NOT_FOUND
