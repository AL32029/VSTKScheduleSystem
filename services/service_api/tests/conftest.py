import asyncio
import os
import pathlib
import subprocess
import sys
from collections.abc import AsyncGenerator, AsyncIterable, Generator
from typing import Any

import pytest
from dishka import make_async_container
from redis.asyncio import Redis
from schedule_db_models import LessonCabinetORM, LessonORM
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from service_api.infrastructure.di.providers import (
    RepositoriesProvider,
    SystemSettingsProvider,
    UseCasesProvider,
)
from service_api.infrastructure.mappers.domain_mappers import (
    cabinet_domain_to_orm,
    group_domain_to_orm,
)
from tests.test_contains import (
    _CABINET_ITEM,
    _CABINET_ITEMS,
    _GROUP_DAY_SCHEDULE_ITEM,
    _GROUP_ITEM,
    _GROUP_ITEMS,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# ====================== [ФИКСТУРЫ БАЗЫ ДАННЫХ] ======================
@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer("postgres:17") as postgres:
        db_url = postgres.get_connection_url(driver="asyncpg")
        os.environ["MIGRATION_DATABASE_URL"] = db_url
        project_root = pathlib.Path(__file__).parent.parent.parent.parent
        subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                str(project_root / "schedule_alembic.ini"),
                "upgrade",
                "head",
            ],
            check=True,
            env=os.environ,
        )
        yield postgres


@pytest.fixture(scope="function")
async def async_engine(postgres_container) -> AsyncIterable[AsyncEngine]:
    """Database engine"""
    engine = create_async_engine(
        postgres_container.get_connection_url(driver="asyncpg"),
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def session_maker(async_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(async_engine, expire_on_commit=False)


@pytest.fixture(scope="function")
async def session_with_test_data(session_maker):
    groups_orm = (group_domain_to_orm(x) for x in {_GROUP_ITEM, *_GROUP_ITEMS})
    cabinets_orm = (cabinet_domain_to_orm(x) for x in {_CABINET_ITEM, *_CABINET_ITEMS})

    async with session_maker() as session:
        session.add_all(
            [
                *groups_orm,
                *cabinets_orm,
                *[
                    LessonORM(
                        group_index=_GROUP_ITEM.index,
                        date=_GROUP_DAY_SCHEDULE_ITEM.date,
                        start=lesson.start,
                        end=lesson.end,
                        name=lesson.name,
                        cabinet_relationships=[
                            LessonCabinetORM(
                                cabinet_id=cabinet.index, cabinet_index=idx
                            )
                            for idx, cabinet in enumerate(lesson.cabinets)
                        ],
                    )
                    for lesson in _GROUP_DAY_SCHEDULE_ITEM.lessons
                ],
            ]
        )
        yield session
        await session.rollback()


# ====================== [ФИКСТУРЫ REDIS] ======================
@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, Any, None]:
    with RedisContainer("redis:8.6.3") as redis:
        yield redis


# ====================== [ФИКСТУРА С ПРОВАЙДЕРАМИ] ======================
@pytest.fixture(scope="function")
async def test_container(request, session_with_test_data, redis_container):
    from dishka import Provider, Scope, provide

    # ====================== [ПРОВАЙДЕР БД] ======================
    class TestDatabaseProvider(Provider):
        scope = Scope.REQUEST

        @provide
        async def provide_session(self) -> AsyncIterable[AsyncSession]:
            """Database session"""
            yield session_with_test_data

    # ====================== [ПРОВАЙДЕР REDIS] ======================
    class TestRedisProvider(Provider):
        scope = Scope.REQUEST

        @provide
        async def redis_client(self) -> AsyncGenerator[Redis, Any]:
            host = redis_container.get_container_host_ip()
            port = redis_container.get_exposed_port(6379)

            client = Redis.from_url(f"redis://{host}:{port}")

            yield client

            await client.delete("group", "schedule")

    container = make_async_container(
        SystemSettingsProvider(),
        TestRedisProvider(),
        TestDatabaseProvider(),
        RepositoriesProvider(),
        UseCasesProvider(),
    )
    yield container
    await container.close()
