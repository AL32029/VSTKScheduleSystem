from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from service_bot.infrastructure.config import (
    APISettings,
    BotSettings,
    DatabaseSettings,
    RedisSettings,
    SystemSettings,
)

from .providers import (
    ClientProvider,
    DatabaseProvider,
    RedisProvider,
    RepositoriesProvider,
    SystemSettingsProvider,
    TemplatesProvider,
    UseCasesProvider,
)


def get_dishka_container() -> "AsyncContainer":
    bot_settings = BotSettings()
    api_settings = APISettings()
    base_system_settings = SystemSettings()
    database_settings = DatabaseSettings()
    redis_settings = RedisSettings()

    container = make_async_container(
        SystemSettingsProvider(),
        AiogramProvider(),
        SystemSettingsProvider(),
        ClientProvider(),
        RedisProvider(),
        DatabaseProvider(),
        RepositoriesProvider(),
        UseCasesProvider(),
        TemplatesProvider(),
        context={
            BotSettings: bot_settings,
            APISettings: api_settings,
            SystemSettings: base_system_settings,
            DatabaseSettings: database_settings,
            RedisSettings: redis_settings,
        },
    )

    return container
