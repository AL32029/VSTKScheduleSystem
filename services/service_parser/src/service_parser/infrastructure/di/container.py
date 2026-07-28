from dishka import make_async_container

from service_parser.infrastructure.config.database import DatabaseSettings
from service_parser.infrastructure.config.redis_settings import RedisSettings
from service_parser.infrastructure.di import DatabaseProvider, RedisProvider
from service_parser.infrastructure.di.providers import HTTPXClientProvider, RepositoriesProvide


def get_dishka_container():
    database_settings = DatabaseSettings()
    redis_settings = RedisSettings()

    return make_async_container(
        DatabaseProvider(),
        RedisProvider(),
        RepositoriesProvide(),
        HTTPXClientProvider(),
        context={DatabaseSettings: database_settings, RedisSettings: redis_settings}
    )
