from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from .providers import (
    DatabaseProvider,
    RedisARQProvider,
    RedisProvider,
    RepositoriesProvider,
    SystemSettingsProvider,
    UseCasesProvider,
)


def get_dishka_container() -> "AsyncContainer":
    """Dishka контейнер зависимостей"""
    return make_async_container(
        SystemSettingsProvider(),
        DatabaseProvider(),
        RedisProvider(),
        RedisARQProvider(),
        RepositoriesProvider(),
        UseCasesProvider(),
        FastapiProvider(),
    )
