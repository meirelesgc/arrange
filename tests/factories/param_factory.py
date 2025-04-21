from datetime import datetime
from uuid import uuid4

import factory

from arrange.models import param_models


class CreateParamFactory(factory.Factory):
    class Meta:
        model = param_models.CreateParam

    name = factory.Faker('word')
    synonyms = factory.List([factory.Faker('word') for _ in range(2)])


class ParamFactory(factory.Factory):
    class Meta:
        model = param_models.Param

    id = factory.LazyFunction(uuid4)
    name = factory.Faker('word')
    synonyms = factory.List([factory.Faker('word') for _ in range(2)])
    created_at = factory.LazyFunction(datetime.now().date())
    updated_at = None
