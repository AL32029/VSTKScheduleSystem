import pytest
from dishka import Scope
from httpx import AsyncClient

from service_bot.application.ports import (
    CabinetRepository,
    GroupRepository,
    ScheduleRepository,
    UserRepository,
)


# ===================== [ФИКСТУРЫ ДЛЯ РЕПОЗИТОРИЕВ] =====================
@pytest.fixture(scope='function')
async def httpx_group_repository(test_container) -> GroupRepository:
    """Репозиторий GroupRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(GroupRepository)


@pytest.fixture(scope='function')
async def httpx_cabinet_repository(test_container) -> CabinetRepository:
    """Репозиторий CabinetRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(CabinetRepository)


@pytest.fixture(scope='function')
async def httpx_schedule_repository(test_container) -> ScheduleRepository:
    """Репозиторий ScheduleRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(ScheduleRepository)


@pytest.fixture(scope='function')
async def sqlalchemy_user_repo(test_container) -> UserRepository:
    """Репозиторий UserRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(UserRepository)


# ===================== [ФИКСТУРЫ ДЛЯ КЛИЕНТОВ] =====================
@pytest.fixture(scope='function')
async def client(test_container):
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(AsyncClient)
