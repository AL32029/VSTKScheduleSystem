import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DevRedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="forbid")

    HOST: str
    PORT: int

    DB_NUMBER: int


class ProdRedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("REDIS_SETTINGS_ENV", "/vault/secrets/redis.env"),
        env_prefix="REDIS_",
        extra="forbid",
    )

    HOST: str
    PORT: int

    DB_NUMBER: int

    SSL_CERT_REQS: Literal["none", "optional", "required"] = Field("required")

    SSL_CERT_FILE: str = Field("/vault/secrets/redis-tls.crt")
    SSL_KEY_FILE: str = Field("/vault/secrets/redis-tls.key")
    SSL_CA_CERT_FILE: str = Field("/vault/secrets/redis-tls.ca")

    SSL_CHECK_HOSTNAME: bool = Field(True)


class RedisSettings:
    def __init__(self, mode: Literal["dev", "prod"] = "dev"):
        self.mode: Literal["dev", "prod"] = mode

        self.dev: "DevRedisSettings" = DevRedisSettings()
        self.prod: "ProdRedisSettings" = ProdRedisSettings()

    @property
    def config(self) -> "DevRedisSettings | ProdRedisSettings":
        return self.dev if self.mode == "dev" else self.prod
