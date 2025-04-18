from http import HTTPStatus


def test_root(client):
    response = client.get('/docs/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []
