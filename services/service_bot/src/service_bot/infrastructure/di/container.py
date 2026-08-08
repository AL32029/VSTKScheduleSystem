from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from service_bot.infrastructure.config import (
    APISettings,
    BaseSystemSettings,
    BotSettings,
    DatabaseSettings,
    RedisSettings,
)

from .providers import (
    ClientProvider,
    DatabaseProvider,
    RedisProvider,
    RepositoriesProvider,
    SystemProvider,
    TemplatesProvider,
    UseCasesProvider,
)


def get_dishka_container() -> 'AsyncContainer':
    bot_settings = BotSettings()
    api_settings = APISettings()
    base_system_settings = BaseSystemSettings()
    database_settings = DatabaseSettings()
    redis_settings = RedisSettings()

    container = make_async_container(
        AiogramProvider(),
        SystemProvider(),
        ClientProvider(),
        RedisProvider(),
        DatabaseProvider(),
        RepositoriesProvider(),
        UseCasesProvider(),
        TemplatesProvider(),
        context={
            BotSettings: bot_settings,
            APISettings: api_settings,
            BaseSystemSettings: base_system_settings,
            DatabaseSettings: database_settings,
            RedisSettings: redis_settings
        }
    )

    return container
