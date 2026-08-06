from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from service_bot.infrastructure.config import BotSettings

from .providers import (
    BotProvider,
    ClientProvider,
    DatabaseProvider,
    RedisProvider,
    RepositoriesProvider,
    TemplatesProvider,
    UseCasesProvider,
)


def get_dishka_container() -> 'AsyncContainer':
    bot_settings = BotSettings()

    container = make_async_container(
        AiogramProvider(),
        BotProvider(),
        ClientProvider(),
        RedisProvider(),
        DatabaseProvider(),
        RepositoriesProvider(),
        UseCasesProvider(),
        TemplatesProvider(),
        context={
            BotSettings: bot_settings
        }
    )

    return container
