from aiolimiter import AsyncLimiter
from dishka import AsyncContainer
from system_managers import RedisClientManager

from service_bot.infrastructure.config import RedisARQSettings
from service_bot.infrastructure.di.container import get_dishka_container

_dishka_container: AsyncContainer = get_dishka_container()
_settings = RedisARQSettings().config
_redis_manager = RedisClientManager(_settings, "arq")
_rate_limiter = AsyncLimiter(30, 2)
