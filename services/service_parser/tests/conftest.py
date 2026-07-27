import os
import pathlib
import subprocess
from typing import AsyncIterable, Any, Generator

import pytest
from dishka import make_async_container
from pydantic import PostgresDsn
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from service_parser.application.ports import CabinetRepository, GroupRepository, ScheduleRepository
from service_parser.infrastructure.config.database import DatabaseSettings
from service_parser.infrastructure.di.providers import HTTPXClientProvider
from service_parser.infrastructure.repositories import SQLAlchemyCabinetRepository, SQLAlchemyGroupRepository, \
    SQLAlchemyScheduleRepository


# ====================== [ФУНКЦИИ] ======================
async def _truncate_all_tables(async_engine):
    """Функция очистки всех таблиц БД"""
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
async def test_container(request):
    from dishka import Provider, Scope, provide

    # ====================== [ПРОВАЙДЕР БД] ======================
    class TestDatabaseProvider(Provider):
        scope = Scope.APP

        @provide
        def database_settings(self) -> DatabaseSettings:
            """Настройки БД"""
            return DatabaseSettings()

        @provide
        async def database_url(self, settings: DatabaseSettings) -> PostgresDsn:
            """URL БД"""
            return settings.URL

        @provide
        def postgres_container(self) -> Generator[PostgresContainer, Any, None]:
            """Контейнер БД"""
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

        @provide
        async def provide_engine(self, postgres: PostgresContainer) -> AsyncIterable[AsyncEngine]:
            """Database engine"""
            engine = create_async_engine(
                postgres.get_connection_url(driver='asyncpg'),
                echo=False,
                pool_size=5,
                pool_pre_ping=True,
            )
            yield engine
            await engine.dispose()

        @provide
        def provide_session_maker(self, async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
            """Database session maker"""
            return async_sessionmaker(
                async_engine,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

        @provide(scope=Scope.REQUEST)
        async def provide_session(self, async_engine: AsyncEngine,
                                  session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
            """Database session"""
            await _truncate_all_tables(async_engine)

            async with session_maker() as session:
                yield session

    # ====================== [ПРОВАЙДЕР РЕПОЗИТОРИЕВ] ======================
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
