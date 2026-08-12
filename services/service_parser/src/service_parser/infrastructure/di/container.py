from dishka import make_async_container

from service_parser.infrastructure.config import BaseSystemSettings
from service_parser.infrastructure.di import (
    DatabaseProvider,
    HTTPXClientProvider,
    RedisProvider,
    RepositoriesProvider,
    SystemProvider,
)


def get_dishka_container():
    base_settings = BaseSystemSettings()

    return make_async_container(
        DatabaseProvider(),
        RedisProvider(),
        RepositoriesProvider(),
        HTTPXClientProvider(),
        SystemProvider(),
        context={
            BaseSystemSettings: base_settings
        }
    )
