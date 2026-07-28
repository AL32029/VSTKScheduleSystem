from typing import AsyncIterable, Any, AsyncGenerator

import httpx
from dishka import Provider, Scope, provide
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from service_parser.application.ports import CabinetRepository, GroupRepository, ScheduleRepository
from service_parser.infrastructure.config.database import DatabaseSettings
from service_parser.infrastructure.config.redis_settings import RedisSettings
from service_parser.infrastructure.repositories import SQLAlchemyCabinetRepository, SQLAlchemyGroupRepository, \
    SQLAlchemyScheduleRepository


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_engine(self, settings: DatabaseSettings) -> AsyncEngine:
        return create_async_engine(
            settings.URL.unicode_string(),
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )

    @provide
    def provide_session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        )

    @provide
    async def provide_session(self, session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def redis_engine(self, settings: RedisSettings) -> AsyncIterable[Redis]:
        client = Redis.from_url(
            settings.URL.unicode_string()
        )
        yield client
        await client.aclose()


class RepositoriesProvide(Provider):
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


class HTTPXClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_client(self) -> AsyncGenerator[AsyncClient, Any]:
        async with httpx.AsyncClient() as client:
            yield client
