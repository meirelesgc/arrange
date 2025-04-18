from http import HTTPStatus

from tests.factories import user_factory


def test_post_user(client):
    user = user_factory.UserFactory()
    response = client.post('/user/', json=user.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.CREATED
