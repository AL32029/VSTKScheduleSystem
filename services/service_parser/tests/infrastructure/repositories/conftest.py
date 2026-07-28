import pytest
from dishka import Scope

from service_parser.application.ports import GroupRepository, CabinetRepository, ScheduleRepository


# ===================== [ФИКСТУРЫ ДЛЯ РЕПОЗИТОРИЯ ГРУППЫ] =====================
@pytest.fixture(scope='function')
async def sqlalchemy_group_repo(test_container) -> GroupRepository:
    """Репозиторий GroupRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(GroupRepository)


@pytest.fixture(scope='function')
async def sqlalchemy_cabinet_repo(test_container) -> CabinetRepository:
    """Репозиторий CabinetRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(CabinetRepository)


@pytest.fixture(scope='function')
async def sqlalchemy_schedule_repo(test_container) -> ScheduleRepository:
    """Репозиторий ScheduleRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(ScheduleRepository)
