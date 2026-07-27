import pytest
from dishka import Scope
from httpx import AsyncClient

from service_parser.infrastructure.clients import HTTPXScheduleProvider


@pytest.fixture
async def client(test_container):
    """Dishka containers client"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(AsyncClient)


@pytest.fixture
def schedule_provider(client):
    """HTTPX Schedule Provider"""
    yield HTTPXScheduleProvider(client, schedule_type='tomorrow')
