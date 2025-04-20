from http import HTTPStatus
from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_post_doc(client, create_user, get_token):
    user = await create_user()
    token = get_token(user)
    file = {'file': ('pdf.pdf', b'pdf', 'application/pdf')}

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
