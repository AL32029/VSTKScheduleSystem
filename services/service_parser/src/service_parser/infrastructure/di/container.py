from dishka import make_async_container

from service_parser.infrastructure.di import (
    DatabaseProvider,
    HTTPXClientProvider,
    RedisProvider,
    RepositoriesProvide,
)


def get_dishka_container():
    return make_async_container(
        DatabaseProvider(),
        RedisProvider(),
        RepositoriesProvide(),
        HTTPXClientProvider(),
    )
