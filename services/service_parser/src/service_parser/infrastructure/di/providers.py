import logging
from collections.abc import AsyncGenerator, AsyncIterable, AsyncIterator
from typing import Annotated, Any, cast
from zoneinfo import ZoneInfo

import httpx
from arq import ArqRedis
from dishka import FromComponent, Provider, Scope, provide
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from system_managers import DatabaseEngineManager, RedisClientManager

from service_parser.application.ports import (
    CabinetRepository,
    GroupRepository,
    MetricsCollector,
    ScheduleRepository,
    TasksRepository,
)
from service_parser.infrastructure.config import (
    DatabaseSettings,
    RedisARQSettings,
    RedisSettings,
    SystemSettings,
)
from service_parser.infrastructure.prometheus_collector import (
    PrometheusMetricsCollector,
)
from service_parser.infrastructure.repositories import (
    ARQTasksRepository,
    SQLAlchemyCabinetRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyScheduleRepository,
)

logger = logging.getLogger(__name__)


class SystemSettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def time_zone(self, base_settings: SystemSettings) -> ZoneInfo:
        return base_settings.timezone

    @provide
    def system_settings(self) -> "SystemSettings":
        return SystemSettings()

    @provide
    def metrics_collector(self) -> "MetricsCollector":
        return PrometheusMetricsCollector()


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    def database_settings(self, settings: "SystemSettings") -> "DatabaseSettings":
        return DatabaseSettings(settings.SYSTEM_MODE)

    @provide
    def database_engine_manager(
        self, settings: "DatabaseSettings"
    ) -> "DatabaseEngineManager":
        logger.debug("Creating DatabaseEngineManager")
        return DatabaseEngineManager(settings.config)

    @provide(scope=Scope.REQUEST)
    async def provide_session_maker(
        self, manager: "DatabaseEngineManager"
    ) -> async_sessionmaker[AsyncSession]:
        logger.debug("Creating database session maker")
        return async_sessionmaker(
            cast(AsyncEngine, cast(object, await manager.get_engine())),
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        metrics: "MetricsCollector",
    ) -> AsyncIterable[AsyncSession]:
        logger.debug("Creating database session")
        async with session_maker() as session:
            metrics.inc_gauge("database_active_sessions_count")
            try:
                yield session

                await session.commit()
            finally:
                await session.aclose()

                metrics.dec_gauge("database_active_sessions_count")


class RedisProvider(Provider):
    scope = Scope.APP
    component = "redis_main"

    @provide
    def redis_settings(
        self, settings: Annotated["SystemSettings", FromComponent("")]
    ) -> "RedisSettings":
        return RedisSettings(settings.SYSTEM_MODE)

    @provide
    def redis_client_manager(self, settings: "RedisSettings") -> "RedisClientManager":
        logger.debug("Creating RedisClientManager for main redis")
        return RedisClientManager(settings.config, "main")

    @provide(scope=Scope.REQUEST)
    async def provide_redis_client(
        self,
        manager: "RedisClientManager",
        metrics: Annotated["MetricsCollector", FromComponent("")],
    ) -> AsyncIterator[Redis]:
        client = await manager.get_client()
        metrics.inc_gauge("redis_active_sessions_count", redis_type="main")
        try:
            yield client
        finally:
            metrics.dec_gauge("redis_active_sessions_count", redis_type="main")


class RedisARQProvider(Provider):
    scope = Scope.APP
    component = "redis_arq"

    @provide
    def redis_settings(
        self, settings: Annotated["SystemSettings", FromComponent("")]
    ) -> "RedisARQSettings":
        return RedisARQSettings(settings.SYSTEM_MODE)

    @provide
    def redis_client_manager(
        self, settings: "RedisARQSettings"
    ) -> "RedisClientManager":
        logger.debug("Creating RedisClientManager for ARQ")
        return RedisClientManager(settings.config, "arq")

    @provide(scope=Scope.REQUEST)
    async def provide_redis_client(
        self,
        manager: "RedisClientManager",
        metrics: Annotated["MetricsCollector", FromComponent("")],
    ) -> AsyncIterator[ArqRedis]:
        client = await manager.get_client()
        metrics.inc_gauge("redis_active_sessions_count", redis_type="arq")
        try:
            yield client
        finally:
            metrics.dec_gauge("redis_active_sessions_count", redis_type="arq")


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def sqlalchemy_cabinet_repository(
        self, session: "AsyncSession"
    ) -> "CabinetRepository":
        return SQLAlchemyCabinetRepository(session)

    @provide
    async def sqlalchemy_group_repository(
        self, session: "AsyncSession"
    ) -> "GroupRepository":
        return SQLAlchemyGroupRepository(session)

    @provide
    async def sqlalchemy_schedule_repository(
        self, session: "AsyncSession"
    ) -> "ScheduleRepository":
        return SQLAlchemyScheduleRepository(session)

    @provide
    async def arq_tasks_repository(
        self, client: Annotated[ArqRedis, FromComponent("redis_arq")]
    ) -> "TasksRepository":
        return ARQTasksRepository(client)


class HTTPXClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_client(self) -> AsyncGenerator["AsyncClient", Any]:
        logger.debug("Creating HTTPX client")
        async with httpx.AsyncClient() as client:
            yield client
