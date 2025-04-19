from http import HTTPStatus

import pytest

from arrange.models import user_models
from tests.factories import user_factory


def test_post_user(client):
    user = user_factory.UserFactory()
    response = client.post('/user/', json=user.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.CREATED
    assert user_models.User(**response.json())


def test_get_users(client):
    LENGTH = 0
    response = client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_one_users(client, create_user):
    LENGTH = 1

    for _ in range(0, LENGTH):
        await create_user()

    response = client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_two_users(client, create_user):
    LENGTH = 2

    for _ in range(0, LENGTH):
        await create_user()

    response = client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_single_user(client, create_user):
    user = await create_user()
    response = client.get(f'/user/{user.id}/')
    assert response.status_code == HTTPStatus.OK
    assert user_models.User(**response.json())
