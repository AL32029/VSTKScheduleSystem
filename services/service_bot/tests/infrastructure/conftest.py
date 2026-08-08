import asyncio
import os
import pathlib
import subprocess
import sys
from collections.abc import AsyncGenerator, AsyncIterable, Generator
from typing import Any

import pytest
from dishka import make_async_container
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from service_bot.application.ports import (
    CabinetRepository,
    GroupRepository,
    ScheduleRepository,
    UserRepository,
)
from service_bot.infrastructure.repositories import (
    HTTPXCabinetRepository,
    HTTPXGroupRepository,
    HTTPXScheduleRepository,
    SQLAlchemyUserRepository,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# ====================== [ФИКСТУРЫ БАЗЫ ДАННЫХ] ======================
@pytest.fixture(scope='session')
def postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer('postgres:17') as postgres:
        db_url = postgres.get_connection_url(driver='asyncpg')
        os.environ["MIGRATION_DATABASE_URL"] = db_url
        project_root = pathlib.Path(__file__).parent.parent.parent
        subprocess.run(
            ["alembic", "-c", str(project_root / "alembic.ini"), "upgrade", "head"],
            check=True,
            env=os.environ,
        )
        yield postgres


@pytest.fixture(scope='function')
async def async_engine(postgres_container) -> AsyncIterable[AsyncEngine]:
    """Database engine"""
    engine = create_async_engine(
        postgres_container.get_connection_url(driver='asyncpg'),
        echo=False,
        pool_size=5,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope='function')
async def session_maker(async_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        async_engine,
        expire_on_commit=False
    )


@pytest.fixture(scope='function')
async def session_with_test_data(session_maker):
    # groups_orm = (GroupO for x in {*_GROUP_ITEMS})
    # cabinets_orm = (cabinet_domain_to_orm(x) for x in {*_CABINET_ITEMS})

    async with session_maker() as session:
        # session.add_all([
        #     *groups_orm, *cabinets_orm,
        #     *[LessonORM(group_index=_GROUP_ITEM.index, date=_GROUP_DAY_SCHEDULE_ITEM.date, start=lesson.start,
        #                 end=lesson.end, name=lesson.name, cabinet_relationships=[
        #             LessonCabinetORM(cabinet_id=cabinet.index, cabinet_index=idx)
        #             for idx, cabinet in enumerate(lesson.cabinets)
        #         ])
        #       for lesson in _GROUP_DAY_SCHEDULE_ITEM.lessons]
        # ])
        yield session
        await session.rollback()


# ====================== [ФИКСТУРЫ REDIS] ======================
@pytest.fixture(scope='session')
def redis_container() -> Generator[RedisContainer, Any, None]:
    with RedisContainer('redis:8.6.3') as redis:
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

            await session_with_test_data.rollback()

    # ====================== [ПРОВАЙДЕР REDIS] ======================
    class TestRedisProvider(Provider):
        scope = Scope.REQUEST

        @provide
        def redis_client(self) -> Generator[Redis, Any, None]:
            host = redis_container.get_container_host_ip()
            port = redis_container.get_exposed_port(6379)
            yield Redis.from_url(f"redis://{host}:{port}")

    # ====================== [ПРОВАЙДЕР HTTPX] ======================
    class ClientProvider(Provider):
        scope = Scope.APP

        @provide
        async def httpx_client(self) -> AsyncGenerator['AsyncClient']:
            async with AsyncClient(base_url='http://test') as client:
                yield client

    # ====================== [ПРОВАЙДЕР РЕПОЗИТОРИЕВ] ======================
    class TestRepositoriesProvider(Provider):
        scope = Scope.REQUEST

        @provide
        def httpx_group_repository(self, client: 'AsyncClient') -> 'GroupRepository':
            return HTTPXGroupRepository(client)

        @provide
        def httpx_cabinet_repository(self, client: 'AsyncClient') -> 'CabinetRepository':
            return HTTPXCabinetRepository(client)

        @provide
        def httpx_schedule_repository(self, client: 'AsyncClient') -> 'ScheduleRepository':
            return HTTPXScheduleRepository(client)

        @provide
        def sqlalchemy_user_repository(self, session: 'AsyncSession') -> 'UserRepository':
            return SQLAlchemyUserRepository(session)

    container = make_async_container(
        ClientProvider(),
        TestRedisProvider(),
        TestDatabaseProvider(),
        TestRepositoriesProvider()
    )
    await container.get(AsyncClient)
    yield container

    # async with async_engine.connect() as conn:
    #     await conn.execute(text("SET session_replication_role = 'replica';"))
    #     result = await conn.execute(text(
    #         "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
    #         "AND tablename != 'alembic_version';"
    #     ))
    #     tables = [row[0] for row in result]
    #     for table in tables:
    #         await conn.execute(text(f'DELETE FROM "{table}";'))
    #     await conn.execute(text("SET session_replication_role = 'origin';"))
    #     await conn.commit()
    #
    # await container.close()
