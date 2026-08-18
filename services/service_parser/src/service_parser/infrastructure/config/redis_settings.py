import os
from typing import Literal

from pydantic_settings import SettingsConfigDict
from system_managers import BaseDevRedisSettings, BaseProdRedisSettings


class DevRedisSettings(BaseDevRedisSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="forbid")


class ProdRedisSettings(BaseProdRedisSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("REDIS_SETTINGS_ENV", "/vault/secrets/redis.env"),
        env_prefix="REDIS_",
        extra="forbid",
    )


class RedisSettings:
    def __init__(self, mode: Literal["dev", "prod"] = "dev"):
        self.mode: Literal["dev", "prod"] = mode

        self.dev: BaseDevRedisSettings = DevRedisSettings()
        self.prod: BaseProdRedisSettings = ProdRedisSettings()

    @property
    def config(self) -> "BaseDevRedisSettings | BaseProdRedisSettings":
        return self.dev if self.mode == "dev" else self.prod

class DevRedisARQSettings(BaseDevRedisSettings):
    model_config = SettingsConfigDict(env_prefix="ARQ_REDIS_", extra="forbid")


class ProdRedisARQSettings(BaseProdRedisSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ARQ_REDIS_SETTINGS_ENV", "/vault/secrets/redis.env"),
        env_prefix="ARQ_REDIS_",
        extra="forbid",
    )


class RedisARQSettings:
    def __init__(self, mode: Literal["dev", "prod"] = "dev"):
        self.mode: Literal["dev", "prod"] = mode

        self.dev: DevRedisARQSettings = DevRedisARQSettings()
        self.prod: ProdRedisARQSettings = ProdRedisARQSettings()

    @property
    def config(self) -> "DevRedisARQSettings | ProdRedisARQSettings":
        return self.dev if self.mode == "dev" else self.prod
