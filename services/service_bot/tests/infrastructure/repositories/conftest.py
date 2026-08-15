import random

import pytest
from dishka import Scope
from httpx import AsyncClient
from sqlalchemy import delete

from service_bot.application.ports import (
    CabinetRepository,
    GroupRepository,
    ScheduleRepository,
    UserRepository,
)
from service_bot.domain.entities import User
from service_bot.infrastructure.db import UserMetadataORM
from service_bot.infrastructure.repositories import SQLAlchemyUserRepository
from tests.test_contains import _CABINET_ITEM, _GROUP_ITEM, _USER_ID


# ===================== [ФИКСТУРЫ ДЛЯ РЕПОЗИТОРИЕВ] =====================
@pytest.fixture(scope="function")
async def httpx_group_repository(test_container) -> "GroupRepository":
    """Репозиторий GroupRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(GroupRepository)


@pytest.fixture(scope="function")
async def httpx_cabinet_repository(test_container) -> CabinetRepository:
    """Репозиторий CabinetRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(CabinetRepository)


@pytest.fixture(scope="function")
async def httpx_schedule_repository(test_container) -> "ScheduleRepository":
    """Репозиторий ScheduleRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(ScheduleRepository)


@pytest.fixture(scope="function")
async def sqlalchemy_user_repo(test_container) -> "UserRepository":
    """Репозиторий UserRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        return await container.get(UserRepository)


# ===================== [ФИКСТУРЫ ДЛЯ КЛИЕНТОВ] =====================
@pytest.fixture(scope="function")
async def client(test_container):
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(AsyncClient)


# ===================== [ФИКСТУРЫ СОХРАНЕННЫХ ДАННЫХ] =====================
@pytest.fixture(scope="function")
async def saved_user(sqlalchemy_user_repo) -> "User":
    return await sqlalchemy_user_repo.save(_USER_ID)


@pytest.fixture(scope="function")
async def saved_user_without_metadata(
    sqlalchemy_user_repo: "SQLAlchemyUserRepository",
) -> tuple["User", str]:
    user = await sqlalchemy_user_repo.save(_USER_ID)

    deleted_metadata = random.choice(list(User._REQUIRED_METADATA))

    await sqlalchemy_user_repo.session.execute(
        delete(UserMetadataORM).where(
            UserMetadataORM.user_id == _USER_ID, UserMetadataORM.key == deleted_metadata
        )
    )

    await sqlalchemy_user_repo.session.commit()

    sqlalchemy_user_repo.session.expire_all()

    del user.metadata[deleted_metadata]

    return user, deleted_metadata


@pytest.fixture(scope="function")
async def saved_user_with_subscribed_group(sqlalchemy_user_repo) -> "User":
    user = await sqlalchemy_user_repo.save(_USER_ID)

    await sqlalchemy_user_repo.subscribe_group(user, _GROUP_ITEM)

    return user


@pytest.fixture(scope="function")
async def saved_user_with_subscribed_cabinet(sqlalchemy_user_repo) -> "User":
    user = await sqlalchemy_user_repo.save(_USER_ID)

    await sqlalchemy_user_repo.subscribe_cabinet(user, _CABINET_ITEM)

    return user
