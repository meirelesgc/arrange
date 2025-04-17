import pytest
from fastapi.testclient import TestClient

from arrange.app import app


@pytest.fixture
def client():
    return TestClient(app)
