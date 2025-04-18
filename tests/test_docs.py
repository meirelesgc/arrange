from http import HTTPStatus


def test_root(client):
    response = client.get('/doc/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []
