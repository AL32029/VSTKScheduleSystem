import asyncio
import os
import pathlib
import subprocess
import sys
from collections.abc import AsyncIterable, Generator
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from dishka import Scope, make_async_container
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from service_parser.application.ports import (
    CabinetRepository,
    GroupRepository,
    ScheduleProvider,
    ScheduleRepository,
)
from service_parser.application.services import ScheduleParserUseCase
from service_parser.infrastructure.clients import HTTPXScheduleProvider
from service_parser.infrastructure.di import HTTPXClientProvider
from service_parser.infrastructure.repositories import (
    SQLAlchemyCabinetRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyScheduleRepository,
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


@pytest.fixture
async def async_engine(postgres_container) -> AsyncIterable[AsyncEngine]:
    """Database engine"""
    engine = create_async_engine(
        postgres_container.get_connection_url(driver="asyncpg"),
        echo=False,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


# ====================== [ФИКСТУРЫ REDIS] ======================
@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, Any, None]:
    with RedisContainer("redis:8.6.3") as redis:
        yield redis


# ====================== [ФИКСТУРА С ПРОВАЙДЕРАМИ] ======================
@pytest.fixture
async def test_container(request, async_engine, redis_container):  # noqa: ARG001
    from dishka import Provider, Scope, provide

    # ====================== [ПРОВАЙДЕР СИСТЕМА] ======================
    class TestSystemProvider(Provider):
        scope = Scope.APP

        @provide
        def time_zone(self) -> ZoneInfo:
            return ZoneInfo("Europe/Minsk")

    # ====================== [ПРОВАЙДЕР БД] ======================
    class TestDatabaseProvider(Provider):
        scope = Scope.REQUEST

        @provide
        async def provide_session(self) -> AsyncIterable[AsyncSession]:
            """Database session"""
            async_session = async_sessionmaker(
                async_engine,
                expire_on_commit=False,
            )
            async with async_session() as session:
                yield session
                await session.rollback()

    # ====================== [ПРОВАЙДЕР REDIS] ======================
    class TestRedisProvider(Provider):
        scope = Scope.REQUEST

        @provide
        def redis_client(self) -> Generator[Redis, Any, None]:
            host = redis_container.get_container_host_ip()
            port = redis_container.get_exposed_port(6379)
            yield Redis.from_url(f"redis://{host}:{port}")

    # ====================== [ПРОВАЙДЕР РЕПОЗИТОРИЕВ] ======================
    class TestRepositoriesProvide(Provider):
        scope = Scope.REQUEST

        @provide
        async def sqlalchemy_cabinet_repository(
            self, session: AsyncSession
        ) -> CabinetRepository:
            return SQLAlchemyCabinetRepository(session)

        @provide
        async def sqlalchemy_group_repository(
            self, session: AsyncSession
        ) -> GroupRepository:
            return SQLAlchemyGroupRepository(session)

        @provide
        async def sqlalchemy_schedule_repository(
            self, session: AsyncSession
        ) -> ScheduleRepository:
            return SQLAlchemyScheduleRepository(session)

        @provide
        async def httpx_schedule_provider(
            self, httpx_client: AsyncClient, redis_client: Redis, timezone: ZoneInfo
        ) -> ScheduleProvider:
            return HTTPXScheduleProvider(
                httpx_client, redis_client, timezone, "tomorrow"
            )

    # ====================== [ПРОВАЙДЕР USECASE'ов] ======================
    class TestUseCasesProvider(Provider):
        scope = Scope.REQUEST

        @provide
        async def schedule_parser_use_case(
            self,
            group_repo: GroupRepository,
            cabinet_repo: CabinetRepository,
            schedule_repo: ScheduleRepository,
            schedule_provider: ScheduleProvider,
        ) -> "ScheduleParserUseCase":
            return ScheduleParserUseCase(
                group_repo, cabinet_repo, schedule_repo, schedule_provider
            )

    container = make_async_container(
        TestSystemProvider(),
        HTTPXClientProvider(),
        TestRedisProvider(),
        TestDatabaseProvider(),
        TestRepositoriesProvide(),
        TestUseCasesProvider(),
    )
    await container.get(AsyncClient)
    yield container

    await container.close()

    async with async_engine.connect() as conn:
        await conn.execute(text("SET session_replication_role = 'replica';"))
        result = await conn.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                "AND tablename != 'alembic_version';"
            )
        )
        tables = [row[0] for row in result]
        for table in tables:
            await conn.execute(text(f'DELETE FROM "{table}";'))
        await conn.execute(text("SET session_replication_role = 'origin';"))
        await conn.commit()


# ======================== [ФИКСТУРА СЕССИИ БД] =========================
@pytest.fixture
async def sqlalchemy_session(test_container) -> AsyncIterable[AsyncSession]:
    """Сессия базы данных"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(AsyncSession)


# ===================== [ФИКСТУРЫ ДЛЯ РЕПОЗИТОРИЕВ] =====================
@pytest.fixture
async def sqlalchemy_group_repo(test_container) -> AsyncIterable["GroupRepository"]:
    """Репозиторий GroupRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(GroupRepository)


@pytest.fixture
async def sqlalchemy_cabinet_repo(test_container) -> AsyncIterable["CabinetRepository"]:
    """Репозиторий CabinetRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(CabinetRepository)


@pytest.fixture
async def sqlalchemy_schedule_repo(
    test_container,
) -> AsyncIterable["ScheduleRepository"]:
    """Репозиторий ScheduleRepository"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(ScheduleRepository)


# ===================== [ФИКСТУРЫ ДЛЯ ПРОВАЙДЕРОВ] =====================
@pytest.fixture
async def schedule_parser_use_case(
    test_container,
) -> AsyncIterable["ScheduleParserUseCase"]:
    """UseCase ScheduleParserUseCase"""
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(ScheduleParserUseCase)
