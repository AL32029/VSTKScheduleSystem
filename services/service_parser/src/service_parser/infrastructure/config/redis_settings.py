import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# TODO: Вернуть название после завершения разработки системы
class ProdRedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.getenv('REDIS_SETTINGS_ENV', '/vault/secrets/database.env'),
                                      env_prefix='REDIS_', extra='ignore')

    SSL_CERT_FILE: str = Field(default='/vault/secrets/redis-tls.crt')
    SSL_KEY_FILE: str = Field(default='/vault/secrets/redis-tls.key')
    SSL_CA_CERT_FILE: str = Field(default='/vault/secrets/redis-tls.ca')

    SSL_CERT_REQS: Literal['none', 'optional', 'required'] = Field(default='required')

    SSL_CHECK_HOSTNAME: bool = Field(default=True)

    @property
    def HOST(self) -> str:
        return os.getenv('REDIS_HOST')

    @property
    def PORT(self) -> int:
        return int(os.getenv('REDIS_PORT'))

    @property
    def DB_NUMBER(self) -> int:
        return int(os.getenv('REDIS_DB_NUMBER'))


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.getenv('REDIS_SETTINGS_ENV', '/vault/secrets/database.env'),
                                      env_prefix='REDIS_', extra='ignore')

    HOST: str
    PORT: int
    USERNAME: str | None
    PASSWORD: str | None
    DB_NUMBER: int
