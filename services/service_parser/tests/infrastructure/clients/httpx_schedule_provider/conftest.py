from zoneinfo import ZoneInfo

import pytest
from dishka import Scope
from httpx import AsyncClient
from redis.asyncio import Redis

from service_parser.infrastructure.clients import HTTPXScheduleProvider


@pytest.fixture
async def client(test_container):
    """Dishka containers client"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(AsyncClient)


@pytest.fixture
async def redis_client(test_container):
    """Redis containers client"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(Redis)


@pytest.fixture
async def timezone(test_container):
    """Timezone container"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(ZoneInfo)


@pytest.fixture
def schedule_provider(client, redis_client, timezone):
    """HTTPX Schedule Provider"""
    return HTTPXScheduleProvider(
        client, redis_client=redis_client, schedule_type="tomorrow", timezone=timezone
    )
