from dishka import make_async_container

from service_parser.infrastructure.config import SystemSettings

from .providers import (
    DatabaseProvider,
    HTTPXClientProvider,
    RedisARQProvider,
    RedisProvider,
    RepositoriesProvider,
    SystemSettingsProvider,
)


def get_dishka_container():
    base_settings = SystemSettings()

    return make_async_container(
        DatabaseProvider(),
        RedisProvider(),
        RedisARQProvider(),
        RepositoriesProvider(),
        HTTPXClientProvider(),
        SystemSettingsProvider(),
        context={SystemSettings: base_settings},
    )
