from http import HTTPStatus

import pytest

from arrange.models import param_models
from tests.factories import param_factory


def test_post_param(client):
    param = param_factory.CreateParamFactory()
    response = client.post('/param/', json=param.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.CREATED
    assert param_models.Param(**response.json())


def test_get_params(client):
    LENGTH = 0
    response = client.get('/param/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_one_params(client, create_param):
    LENGTH = 1

    for _ in range(0, LENGTH):
        await create_param()

    response = client.get('/param/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_get_two_params(client, create_param):
    LENGTH = 2

    for _ in range(0, LENGTH):
        await create_param()

    response = client.get('/param/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH


@pytest.mark.asyncio
async def test_put_param(client, create_param):
    param = await create_param()
    param.name = 'updated name'
    response = client.put('/param/', json=param.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.OK
    assert param_models.Param(**response.json())
    assert response.json()['updated_at']


@pytest.mark.asyncio
async def test_delete_param(client, create_param):
    param = await create_param()
    response = client.delete(f'/param/{param.id}/')
    assert response.status_code == HTTPStatus.NO_CONTENT

    LENGTH = 0
    response = client.get('/param/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == LENGTH
