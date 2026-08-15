from dishka import make_async_container

from service_parser.infrastructure.config import SystemSettings
from service_parser.infrastructure.di import (
    DatabaseProvider,
    HTTPXClientProvider,
    RedisProvider,
    RepositoriesProvider,
    SystemSettingsProvider,
)


def get_dishka_container():
    base_settings = SystemSettings()

    return make_async_container(
        DatabaseProvider(),
        RedisProvider(),
        RepositoriesProvider(),
        HTTPXClientProvider(),
        SystemSettingsProvider(),
        context={SystemSettings: base_settings},
    )
