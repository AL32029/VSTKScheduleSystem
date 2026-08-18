from dishka import AsyncContainer
from system_managers import RedisClientManager

from service_api.infrastructure.config import RedisARQSettings
from service_api.infrastructure.di.container import get_dishka_container

_dishka_container: AsyncContainer = get_dishka_container()
_settings = RedisARQSettings().config
_redis_manager = RedisClientManager(_settings, "arq")
