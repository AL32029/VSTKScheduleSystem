import logging
import os
from collections.abc import AsyncGenerator, AsyncIterable, AsyncIterator
from typing import cast
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka import Provider, Scope, provide
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from system_managers import DatabaseEngineManager, RedisClientManager, WatchFilesManager

from service_bot.application.ports import (
    CabinetRepository,
    GroupRepository,
    MetricsCollector,
    ScheduleRepository,
    UserRepository,
)
from service_bot.application.services import (
    GetAllCabinetsUseCase,
    GetAllGroupsUseCase,
    GetCabinetUseCase,
    GetDayScheduleUseCase,
    GetGroupUseCase,
    GetUserProfileUseCase,
    SaveUserProfileUseCase,
    SubscribeCabinetUseCase,
    SubscribeGroupUseCase,
    UnsubscribeCabinetUseCase,
    UnsubscribeGroupUseCase,
)
from service_bot.infrastructure.config import (
    APISettings,
    BotSettings,
    DatabaseSettings,
    RedisSettings,
    SystemSettings,
)
from service_bot.infrastructure.prometheus_collector import PrometheusMetricsCollector
from service_bot.infrastructure.repositories import (
    HTTPXCabinetRepository,
    HTTPXGroupRepository,
    HTTPXScheduleRepository,
    SQLAlchemyUserRepository,
)
from service_bot.infrastructure.template_engine_items import (
    TemplateKeyboardRenderer,
    TemplateMessageRenderer,
)

logger = logging.getLogger(__name__)


class SystemSettingsProvider(Provider):
    """Провайдер системных зависимостей"""

    scope = Scope.APP

    @provide
    def bot_client(self, bot_settings: BotSettings) -> Bot:
        """Зависимость получения класса чат-бота aiogram.Bot"""
        return Bot(
            token=bot_settings.TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    @provide
    def time_zone(self, base_settings: SystemSettings) -> ZoneInfo:
        return base_settings.timezone

    @provide
    def system_settings(self) -> "SystemSettings":
        return SystemSettings()

    @provide
    def metrics_collector(self) -> "MetricsCollector":
        return PrometheusMetricsCollector()

    @provide
    def watchfiles_manager(
        self,
        db_settings: "DatabaseSettings",
        redis_settings: "RedisSettings",
    ) -> "WatchFilesManager":
        return WatchFilesManager(db_settings.config, redis_settings.config)


class ClientProvider(Provider):
    """Провайдер клиентов для взаимодействия с внешними зависимостями"""

    scope = Scope.APP

    @provide
    async def httpx_client(
        self,
        settings: "APISettings",
    ) -> AsyncGenerator["AsyncClient"]:
        """Зависимость получения класса httpx.AsyncClient"""
        logger.debug("Creating HTTPX client with base URL: %s", settings.SCHEDULE_URL)
        async with AsyncClient(base_url=settings.SCHEDULE_URL) as client:
            yield client


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

    @provide
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
    """Провайдер репозиториев"""

    scope = Scope.REQUEST

    @provide
    def httpx_group_repository(self, client: "AsyncClient") -> "GroupRepository":
        return HTTPXGroupRepository(client)

    @provide
    def httpx_cabinet_repository(self, client: "AsyncClient") -> "CabinetRepository":
        return HTTPXCabinetRepository(client)

    @provide
    def httpx_schedule_repository(self, client: "AsyncClient") -> "ScheduleRepository":
        return HTTPXScheduleRepository(client)

    @provide
    def sqlalchemy_user_repository(self, session: "AsyncSession") -> "UserRepository":
        return SQLAlchemyUserRepository(session)


class UseCasesProvider(Provider):
    """Провайдер usecase'ов"""

    scope = Scope.REQUEST

    @provide
    def get_group_use_case(self, repo: "GroupRepository") -> "GetGroupUseCase":
        return GetGroupUseCase(repo)

    @provide
    def get_all_groups_use_case(self, repo: "GroupRepository") -> "GetAllGroupsUseCase":
        return GetAllGroupsUseCase(repo)

    @provide
    def get_cabinet_use_case(self, repo: "CabinetRepository") -> "GetCabinetUseCase":
        return GetCabinetUseCase(repo)

    @provide
    def get_all_cabinets_use_case(
        self,
        repo: "CabinetRepository",
    ) -> "GetAllCabinetsUseCase":
        return GetAllCabinetsUseCase(repo)

    @provide
    def get_user_profile_use_case(
        self,
        repo: "UserRepository",
    ) -> "GetUserProfileUseCase":
        return GetUserProfileUseCase(repo)

    @provide
    def save_user_profile_use_case(
        self,
        repo: "UserRepository",
    ) -> "SaveUserProfileUseCase":
        return SaveUserProfileUseCase(repo)

    @provide
    def subscribe_group_use_case(
        self,
        repo: "UserRepository",
    ) -> "SubscribeGroupUseCase":
        return SubscribeGroupUseCase(repo)

    @provide
    def subscribe_cabinet_use_case(
        self,
        repo: "UserRepository",
    ) -> "SubscribeCabinetUseCase":
        return SubscribeCabinetUseCase(repo)

    @provide
    def unsubscribe_group_use_case(
        self,
        repo: "UserRepository",
    ) -> "UnsubscribeGroupUseCase":
        return UnsubscribeGroupUseCase(repo)

    @provide
    def unsubscribe_cabinet_use_case(
        self,
        repo: "UserRepository",
    ) -> "UnsubscribeCabinetUseCase":
        return UnsubscribeCabinetUseCase(repo)

    @provide
    def get_day_schedule(self, repo: "ScheduleRepository") -> "GetDayScheduleUseCase":
        return GetDayScheduleUseCase(repo)


class TemplatesProvider(Provider):
    """Провайдер шаблонизаторов"""

    scope = Scope.APP

    @provide
    def template_message_render(self) -> "TemplateMessageRenderer":
        logger.debug(
            "Initializing message template renderer from %s",
            os.getenv("TEMPLATES_FOLDER_PATH", "/app/templates"),
        )
        return TemplateMessageRenderer(
            os.getenv("TEMPLATES_FOLDER_PATH", "/app/templates"),
        )

    @provide
    def template_keyboard_render(self) -> "TemplateKeyboardRenderer":
        return TemplateKeyboardRenderer()
