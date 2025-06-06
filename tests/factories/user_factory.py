import uuid
from datetime import datetime

import factory

from arrange.models import user_models


class CreateUserFactory(factory.Factory):
    class Meta:
        model = user_models.CreateUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')


class UserFactory(factory.Factory):
    class Meta:
        model = user_models.User

    id = factory.LazyFunction(uuid.uuid4)
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    role = 'DEFAULT'
    password = factory.Faker('password')
    created_at = factory.LazyFunction(lambda: datetime.now().date())
    updated_atdate = None
