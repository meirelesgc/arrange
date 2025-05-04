from http import HTTPStatus

import pytest

from arrange.models import arrange_models


@pytest.mark.asyncio
async def test_arrange_details(client, create_doc):
    doc = await create_doc()
    response = client.put(f'/arrange/{doc.id}/details/')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['type'] == 'DETAILS'
    assert response.json()['status'] == 'STANDBY'
    assert arrange_models.Arrange(**response.json())


@pytest.mark.asyncio
async def test_get_arrange_details(client, create_doc):
    doc = await create_doc()
    response = client.get(f'/arrange/{doc.id}/details/')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['type'] == 'DETAILS'
    assert response.json()['status'] == 'STANDBY'
    assert arrange_models.Arrange(**response.json())


@pytest.mark.asyncio
async def test_arrange_patient(client, create_doc):
    doc = await create_doc()
    response = client.put(f'/arrange/{doc.id}/patient/')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['type'] == 'PATIENTS'
    assert response.json()['status'] == 'STANDBY'
    assert arrange_models.Arrange(**response.json())


@pytest.mark.asyncio
async def test_get_arrange_patient(client, create_doc):
    doc = await create_doc()
    response = client.get(f'/arrange/{doc.id}/patient/')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['type'] == 'PATIENTS'
    assert response.json()['status'] == 'STANDBY'
    assert arrange_models.Arrange(**response.json())


@pytest.mark.asyncio
async def test_arrange_metrics_without_params(client, create_doc):
    doc = await create_doc()
    response = client.put(f'/arrange/{doc.id}/metrics/')
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_put_metrics(client, create_doc, create_param):
    doc = await create_doc()
    await create_param()
    response = client.put(f'/arrange/{doc.id}/metrics/')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['type'] == 'METRICS'
    assert response.json()['status'] == 'STANDBY'
    assert arrange_models.Arrange(**response.json())


@pytest.mark.asyncio
async def test_get_metrics(client, create_doc):
    doc = await create_doc()
    response = client.get(f'/arrange/{doc.id}/metrics/')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['type'] == 'METRICS'
    assert response.json()['status'] == 'STANDBY'
    assert arrange_models.Arrange(**response.json())


@pytest.mark.asyncio
async def test_patch_metrics(client, create_doc):
    doc = await create_doc()
    output = {'test': ['test']}
    response = client.patch(f'/arrange/{doc.id}/metrics/', json=output)
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/arrange/{doc.id}/metrics/')
    assert response.json()['output'] == output
