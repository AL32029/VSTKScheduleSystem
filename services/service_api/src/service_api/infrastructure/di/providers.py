from collections.abc import AsyncIterable
from typing import cast

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
    ScheduleRepository,
)
from service_api.application.services import (
    GetAllCabinetsUseCase,
    GetAllGroupsUseCase,
    GetCabinetUseCase,
    GetGroupUseCase,
)
from service_api.application.services.get_cabinet_day_schedule import (
    GetCabinetDayScheduleUseCase,
)
from service_api.application.services.get_group_day_schedule import (
    GetGroupDayScheduleUseCase,
)
from service_api.infrastructure.config import DatabaseSettings, RedisSettings
from service_api.infrastructure.managers import (
    DatabaseEngineManager,
    RedisClientManager,
)
from service_api.infrastructure.repositories import (
    RedisCacheRepository,
    SQLAlchemyCabinetRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyScheduleRepository,
)


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    def database_engine_manager(self) -> 'DatabaseEngineManager':
        settings = DatabaseSettings()
        return DatabaseEngineManager(settings)

    @provide(scope=Scope.REQUEST)
    async def provide_session_maker(self, manager: 'DatabaseEngineManager') -> 'async_sessionmaker[AsyncSession]':
        return async_sessionmaker(
            cast('AsyncEngine', cast(object, await manager.get_engine())),
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(self, session_maker: 'async_sessionmaker[AsyncSession]') -> 'AsyncIterable[AsyncSession]':
        async with session_maker() as session:
            yield session


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    def redis_client_manager(self) -> 'RedisClientManager':
        settings = RedisSettings()
        return RedisClientManager(settings)

    @provide(scope=Scope.REQUEST)
    async def provide_redis_client(self, manager: 'RedisClientManager') -> 'Redis':
        return await manager.get_client()


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def sqlalchemy_group_repository(self, session: 'AsyncSession') -> 'GroupRepository':
        return SQLAlchemyGroupRepository(session)

    @provide
    async def sqlalchemy_cabinet_repository(self, session: 'AsyncSession') -> 'CabinetRepository':
        return SQLAlchemyCabinetRepository(session)

    @provide
    async def sqlalchemy_schedule_repository(self, session: 'AsyncSession') -> 'ScheduleRepository':
        return SQLAlchemyScheduleRepository(session)

    @provide
    async def redis_cache_repository(self, redis_client: 'Redis') -> 'CacheRepository':
        return RedisCacheRepository(redis_client)


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_group_use_case(self, group_repo: 'GroupRepository',
                                 cache_repo: 'CacheRepository') -> 'GetGroupUseCase':
        return GetGroupUseCase(group_repo, cache_repo)

    @provide
    async def get_all_groups_use_case(self, group_repo: 'GroupRepository',
                                      cache_repo: 'CacheRepository') -> 'GetAllGroupsUseCase':
        return GetAllGroupsUseCase(group_repo, cache_repo)

    @provide
    async def get_cabinet_use_case(self, cabinet_repo: 'CabinetRepository',
                                   cache_repo: 'CacheRepository') -> 'GetCabinetUseCase':
        return GetCabinetUseCase(cabinet_repo, cache_repo)

    @provide
    async def get_all_cabinets_use_case(self, repo: 'CabinetRepository',
                                        cache_repo: 'CacheRepository') -> 'GetAllCabinetsUseCase':
        return GetAllCabinetsUseCase(repo, cache_repo)

    @provide
    async def get_group_day_schedule_use_case(self, group_repo: 'GroupRepository',
                                              schedule_repo: 'ScheduleRepository',
                                              cache_repo: 'CacheRepository') -> 'GetGroupDayScheduleUseCase':
        return GetGroupDayScheduleUseCase(group_repo, schedule_repo, cache_repo)

    @provide
    async def get_cabinet_day_schedule_use_case(self, cabinet_repo: 'CabinetRepository',
                                                schedule_repo: 'ScheduleRepository',
                                                cache_repo: 'CacheRepository') -> 'GetCabinetDayScheduleUseCase':
        return GetCabinetDayScheduleUseCase(cabinet_repo, schedule_repo, cache_repo)
