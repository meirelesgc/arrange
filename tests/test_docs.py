from http import HTTPStatus
from pathlib import Path

import pytest


def test_get_doc(client):
    response = client.get('/doc/')
    assert response.status_code == HTTPStatus.OK


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
