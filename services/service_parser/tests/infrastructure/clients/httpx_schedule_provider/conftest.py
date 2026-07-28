import pytest
from dishka import Scope
from httpx import AsyncClient
from redis.asyncio import Redis

from service_parser.infrastructure.clients import HTTPXScheduleProvider


@pytest.fixture(scope='function')
async def client(test_container):
    """Dishka containers client"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(AsyncClient)


@pytest.fixture(scope='function')
async def redis_client(test_container):
    """Redis containers client"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(Redis)


@pytest.fixture
def schedule_provider(client, redis_client):
    """HTTPX Schedule Provider"""
    yield HTTPXScheduleProvider(client, redis_client=redis_client, schedule_type='tomorrow')
