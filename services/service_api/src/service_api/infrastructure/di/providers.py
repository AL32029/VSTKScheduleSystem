import logging
from collections.abc import AsyncIterable
from typing import AsyncIterator, cast

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from service_api.application.ports import (
    CabinetRepository,
    CacheRepository,
    GroupRepository,
    MetricsCollector,
    ScheduleRepository,
)
from service_api.application.services import (
    GetAllCabinetsUseCase,
    GetAllGroupsUseCase,
    GetCabinetDayScheduleUseCase,
    GetCabinetUseCase,
    GetGroupDayScheduleUseCase,
    GetGroupUseCase,
)
from service_api.infrastructure.config import (
    DatabaseSettings,
    RedisSettings,
    SystemSettings,
)
from service_api.infrastructure.managers import (
    DatabaseEngineManager,
    RedisClientManager,
    WatchFilesManager,
)
from service_api.infrastructure.prometheus_collector import PrometheusMetricsCollector
from service_api.infrastructure.repositories import (
    RedisCacheRepository,
    SQLAlchemyCabinetRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyScheduleRepository,
)

logger = logging.getLogger(__name__)


class SystemSettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def system_settings(self) -> "SystemSettings":
        return SystemSettings()

    @provide
    def metrics_collector(self) -> "MetricsCollector":
        return PrometheusMetricsCollector()

    @provide
    def watchfiles_manager(
        self, db_settings: "DatabaseSettings", redis_settings: "RedisSettings"
    ) -> "WatchFilesManager":
        return WatchFilesManager(db_settings.config, redis_settings.config)


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

    @provide
    def redis_settings(self, settings: "SystemSettings") -> "RedisSettings":
        return RedisSettings(settings.SYSTEM_MODE)

    @provide
    def redis_client_manager(self, settings: "RedisSettings") -> "RedisClientManager":
        logger.debug("Creating RedisClientManager")
        return RedisClientManager(settings.config)

    @provide(scope=Scope.REQUEST)
    async def provide_redis_client(
        self,
        manager: "RedisClientManager",
        metrics: "MetricsCollector",
    ) -> AsyncIterator[Redis]:
        client = await manager.get_client()
        metrics.inc_gauge("redis_active_sessions_count")
        try:
            yield client
        finally:
            metrics.dec_gauge("redis_active_sessions_count")


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def sqlalchemy_group_repository(
        self, session: AsyncSession
    ) -> "GroupRepository":
        return SQLAlchemyGroupRepository(session)

    @provide
    async def sqlalchemy_cabinet_repository(
        self, session: AsyncSession
    ) -> "CabinetRepository":
        return SQLAlchemyCabinetRepository(session)

    @provide
    async def sqlalchemy_schedule_repository(
        self, session: AsyncSession
    ) -> "ScheduleRepository":
        return SQLAlchemyScheduleRepository(session)

    @provide
    async def redis_cache_repository(self, redis_client: Redis) -> "CacheRepository":
        return RedisCacheRepository(redis_client)


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def group_use_case(
        self, group_repo: "GroupRepository", cache_repo: "CacheRepository"
    ) -> "GetGroupUseCase":
        return GetGroupUseCase(group_repo, cache_repo)

    @provide
    async def all_groups_use_case(
        self, group_repo: "GroupRepository", cache_repo: "CacheRepository"
    ) -> "GetAllGroupsUseCase":
        return GetAllGroupsUseCase(group_repo, cache_repo)

    @provide
    async def cabinet_use_case(
        self, cabinet_repo: "CabinetRepository", cache_repo: "CacheRepository"
    ) -> "GetCabinetUseCase":
        return GetCabinetUseCase(cabinet_repo, cache_repo)

    @provide
    async def all_cabinets_use_case(
        self, repo: "CabinetRepository", cache_repo: "CacheRepository"
    ) -> "GetAllCabinetsUseCase":
        return GetAllCabinetsUseCase(repo, cache_repo)

    @provide
    async def group_day_schedule_use_case(
        self,
        group_repo: "GroupRepository",
        schedule_repo: "ScheduleRepository",
        cache_repo: "CacheRepository",
    ) -> "GetGroupDayScheduleUseCase":
        return GetGroupDayScheduleUseCase(group_repo, schedule_repo, cache_repo)

    @provide
    async def cabinet_day_schedule_use_case(
        self,
        cabinet_repo: "CabinetRepository",
        schedule_repo: "ScheduleRepository",
        cache_repo: "CacheRepository",
    ) -> "GetCabinetDayScheduleUseCase":
        return GetCabinetDayScheduleUseCase(cabinet_repo, schedule_repo, cache_repo)
