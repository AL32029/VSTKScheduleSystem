from dishka import make_async_container

from service_parser.infrastructure.config.database import DatabaseSettings
from service_parser.infrastructure.di import DatabaseProvider
from service_parser.infrastructure.di.providers import HTTPXClientProvider, RepositoriesProvide


def get_dishka_container():
    database_settings = DatabaseSettings()

    return make_async_container(
        DatabaseProvider(),
        RepositoriesProvide(),
        HTTPXClientProvider(),
        context={DatabaseSettings: database_settings}
    )
