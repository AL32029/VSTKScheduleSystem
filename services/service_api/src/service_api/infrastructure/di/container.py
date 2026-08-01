from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from .providers import (
    DatabaseProvider,
    RedisProvider,
    RepositoriesProvider,
    UseCasesProvider,
)


def get_dishka_container() -> AsyncContainer:
    """Dishka контейнер зависимостей"""
    return make_async_container(
        DatabaseProvider(),
        RedisProvider(),
        RepositoriesProvider(),
        UseCasesProvider(),
        FastapiProvider()
    )
