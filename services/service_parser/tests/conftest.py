import asyncio
import os
import pathlib
import subprocess
import sys
from typing import AsyncIterable

import pytest
from dishka import make_async_container, Scope
from pydantic import PostgresDsn
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from testcontainers.postgres import PostgresContainer

from service_parser.application.ports import CabinetRepository, GroupRepository, ScheduleRepository
from service_parser.infrastructure.di.providers import HTTPXClientProvider
from service_parser.infrastructure.repositories import SQLAlchemyCabinetRepository, SQLAlchemyGroupRepository, \
    SQLAlchemyScheduleRepository

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer('postgres:17') as postgres:
        db_url = postgres.get_connection_url(driver='asyncpg')
        os.environ["MIGRATION_DATABASE_URL"] = db_url
        project_root = pathlib.Path(__file__).parent.parent.parent.parent
        subprocess.run(
            ["alembic", "-c", str(project_root / "schedule_alembic.ini"), "upgrade", "head"],
            check=True,
            env=os.environ,
        )
        yield postgres


async def _truncate_all_tables(async_engine):
    async with async_engine.connect() as conn:
        await conn.execute(text("SET session_replication_role = 'replica';"))
        result = await conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
            "AND tablename != 'alembic_version';"
        ))
        tables = [row[0] for row in result]
        for table in tables:
            await conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;'))
        await conn.execute(text("SET session_replication_role = 'origin';"))
        await conn.commit()


@pytest.fixture(scope="function")
async def test_container(request, postgres_container):
    from dishka import Provider, Scope, provide

    class TestDatabaseProvider(Provider):
        scope = Scope.APP

        @provide
        async def database_url(self) -> PostgresDsn:
            pass

        @provide
        async def provide_engine(self) -> AsyncIterable[AsyncEngine]:
            engine = create_async_engine(
                os.environ["MIGRATION_DATABASE_URL"],
                echo=False,
                pool_size=5,
                pool_pre_ping=True,
            )
            yield engine
            await engine.dispose()

        @provide
        def provide_session_maker(self, async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
            return async_sessionmaker(
                async_engine,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

        @provide(scope=Scope.REQUEST)
        async def provide_session(self, async_engine: AsyncEngine,
                                  session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
            await _truncate_all_tables(async_engine)

            async with session_maker() as session:
                yield session

    class TestRepositoriesProvide(Provider):
        scope = Scope.REQUEST

        @provide
        async def sqlalchemy_cabinet_repository(self, session: AsyncSession) -> CabinetRepository:
            return SQLAlchemyCabinetRepository(session)

        @provide
        async def sqlalchemy_group_repository(self, session: AsyncSession) -> GroupRepository:
            return SQLAlchemyGroupRepository(session)

        @provide
        async def sqlalchemy_schedule_repository(self, session: AsyncSession) -> ScheduleRepository:
            return SQLAlchemyScheduleRepository(session)

    container = make_async_container(
        HTTPXClientProvider(),
        TestDatabaseProvider(),
        TestRepositoriesProvide()
    )
    yield container
    await container.close()


@pytest.fixture
async def group_repository(test_container) -> GroupRepository:
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(GroupRepository)


@pytest.fixture
async def cabinet_repository(test_container) -> SQLAlchemyCabinetRepository:
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(CabinetRepository)


@pytest.fixture
async def schedule_repository(test_container) -> SQLAlchemyScheduleRepository:
    async with test_container(scope=Scope.REQUEST) as container:
        yield await container.get(ScheduleRepository)
