from dishka import make_async_container

from service_parser.infrastructure.config.database import DatabaseSettings
from service_parser.infrastructure.config.redis_settings import RedisSettings
from service_parser.infrastructure.di import DatabaseProvider, RedisProvider
from service_parser.infrastructure.di.providers import HTTPXClientProvider, RepositoriesProvide


def get_dishka_container():
    return make_async_container(
        DatabaseProvider(),
        RedisProvider(),
        RepositoriesProvide(),
        HTTPXClientProvider(),
    )
