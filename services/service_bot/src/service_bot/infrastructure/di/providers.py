from collections.abc import AsyncGenerator, AsyncIterable

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
    create_async_engine,
)

from service_bot.application.ports import (
    CabinetRepository,
    GroupRepository,
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
from service_bot.infrastructure.config import BotSettings
from service_bot.infrastructure.repositories import (
    HTTPXCabinetRepository,
    HTTPXGroupRepository,
    HTTPXScheduleRepository,
    SQLAlchemyUserRepository,
)
from service_bot.infrastructure.template_system import (
    TemplateKeyboardRenderer,
    TemplateMessageRenderer,
)


class BotProvider(Provider):
    """Провайдер чат-бота"""
    scope = Scope.APP

    @provide
    def bot_client(self, bot_settings: BotSettings) -> Bot:
        """Зависимость получения класса чат-бота aiogram.Bot"""
        return Bot(token=bot_settings.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


class ClientProvider(Provider):
    """Провайдер клиентов для взаимодействия с внешними зависимостями"""
    scope = Scope.APP

    @provide
    async def httpx_client(self) -> AsyncGenerator['AsyncClient']:
        """Зависимость получения класса httpx.AsyncClient"""
        async with AsyncClient() as client:
            yield client


class RedisProvider(Provider):
    """Провайдер Redis"""
    scope = Scope.APP

    @provide
    def redis_client(self) -> Redis:
        """Зависимость получения клиента redis.asyncio.Redis"""
        # TODO: Заменить на конфигурацию для продакшена
        return Redis(
            host='localhost',
            port=9999,
            db=2
        )


class DatabaseProvider(Provider):
    """Провайдер базы данных"""
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def database_engine(self) -> AsyncEngine:
        """Зависимость получения движка SQLAlchemy"""
        # TODO: Заменить на конфигурацию для продакшена
        return create_async_engine(
            'postgresql+asyncpg://development:development@localhost:5432/schedule_bot',
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )

    @provide
    def session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        """Зависимость получения session maker SQLAlchemy"""
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @provide
    async def session(self, session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        """Зависимость получения сессии SQLAlchemy"""
        async with session_maker() as session:
            yield session

            await session.commit()


class RepositoriesProvider(Provider):
    """Провайдер репозиториев"""
    scope = Scope.REQUEST

    @provide
    def httpx_group_repository(self, client: 'AsyncClient') -> 'GroupRepository':
        """Зависимость получения репозитория HTTPXGroupRepository"""
        return HTTPXGroupRepository(client)

    @provide
    def httpx_cabinet_repository(self, client: 'AsyncClient') -> 'CabinetRepository':
        """Зависимость получения репозитория HTTPXCabinetRepository"""
        return HTTPXCabinetRepository(client)

    @provide
    def httpx_schedule_repository(self, client: 'AsyncClient') -> 'ScheduleRepository':
        """Зависимость получения репозитория HTTPXScheduleRepository"""
        return HTTPXScheduleRepository(client)

    @provide
    def sqlalchemy_user_repository(self, session: 'AsyncSession') -> 'UserRepository':
        """Зависимость получения репозитория SQLAlchemyUserRepository"""
        return SQLAlchemyUserRepository(session)


class UseCasesProvider(Provider):
    """Провайдер usecase'ов"""
    scope = Scope.REQUEST

    @provide
    def get_group_use_case(self, repo: 'GroupRepository') -> 'GetGroupUseCase':
        """Зависимость получения usecase'а GetGroupUseCase"""
        return GetGroupUseCase(repo)

    @provide
    def get_all_groups_use_case(self, repo: 'GroupRepository') -> 'GetAllGroupsUseCase':
        """Зависимость получения usecase'а GetAllGroupsUseCase"""
        return GetAllGroupsUseCase(repo)

    @provide
    def get_cabinet_use_case(self, repo: 'CabinetRepository') -> 'GetCabinetUseCase':
        """Зависимость получения usecase'а GetCabinetUseCase"""
        return GetCabinetUseCase(repo)

    @provide
    def get_all_cabinets_use_case(self, repo: 'CabinetRepository') -> 'GetAllCabinetsUseCase':
        """Зависимость получения usecase'а GetAllCabinetsUseCase"""
        return GetAllCabinetsUseCase(repo)

    @provide
    def get_user_profile_use_case(self, repo: 'UserRepository') -> 'GetUserProfileUseCase':
        """Зависимость получения usecase'а GetUserProfileUseCase"""
        return GetUserProfileUseCase(repo)

    @provide
    def save_user_profile_use_case(self, repo: 'UserRepository') -> 'SaveUserProfileUseCase':
        """Зависимость получения usecase'а SaveUserProfileUseCase"""
        return SaveUserProfileUseCase(repo)

    @provide
    def subscribe_group_use_case(self, repo: 'UserRepository') -> 'SubscribeGroupUseCase':
        """Зависимость получения usecase'а SubscribeGroupUseCase"""
        return SubscribeGroupUseCase(repo)

    @provide
    def subscribe_cabinet_use_case(self, repo: 'UserRepository') -> 'SubscribeCabinetUseCase':
        """Зависимость получения usecase'а SubscribeCabinetUseCase"""
        return SubscribeCabinetUseCase(repo)

    @provide
    def unsubscribe_group_use_case(self, repo: 'UserRepository') -> 'UnsubscribeGroupUseCase':
        """Зависимость получения usecase'а UnsubscribeGroupUseCase"""
        return UnsubscribeGroupUseCase(repo)

    @provide
    def unsubscribe_cabinet_use_case(self, repo: 'UserRepository') -> 'UnsubscribeCabinetUseCase':
        """Зависимость получения usecase'а UnsubscribeCabinetUseCase"""
        return UnsubscribeCabinetUseCase(repo)

    @provide
    def get_day_schedule(self, repo: 'ScheduleRepository') -> 'GetDayScheduleUseCase':
        """Зависимость получения usecase'а GetDayScheduleUseCase"""
        return GetDayScheduleUseCase(repo)


class TemplatesProvider(Provider):
    """Провайдер шаблонизаторов"""
    scope = Scope.APP

    @provide
    def template_message_render(self) -> 'TemplateMessageRenderer':
        """Зависимость получения шаблонизатора сообщений TemplateMessageRenderer"""
        return TemplateMessageRenderer()

    @provide
    def template_keyboard_render(self) -> 'TemplateKeyboardRenderer':
        """Зависимость получения шаблонизатора клавиатур TemplateKeyboardRenderer"""
        return TemplateKeyboardRenderer()
