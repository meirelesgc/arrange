from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_arrange_details(client, create_doc):
    doc = await create_doc()
    response = client.post(f'/arrange/{doc.id}/details/')
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_arrange_patient(client, create_doc):
    doc = await create_doc()
    response = client.post(f'/arrange/{doc.id}/patient/')
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_arrange_metrics_without_params(client, create_doc):
    doc = await create_doc()
    response = client.post(f'/arrange/{doc.id}/metrics/')
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_arrange_metrics(client, create_doc, create_param):
    doc = await create_doc()
    await create_param()
    response = client.post(f'/arrange/{doc.id}/metrics/')
    assert response.status_code == HTTPStatus.OK
