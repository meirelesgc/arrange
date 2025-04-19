from http import HTTPStatus

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
