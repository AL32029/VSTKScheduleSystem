import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.getenv('REDIS_SETTINGS_ENV', '/vault/secrets/redis.env'),
                                      env_prefix='REDIS_', extra='ignore')

    SSL_CERT_FILE: str = Field(default='/vault/secrets/redis-tls.crt')
    SSL_KEY_FILE: str = Field(default='/vault/secrets/redis-tls.key')
    SSL_CA_CERT_FILE: str = Field(default='/vault/secrets/redis-tls.ca')

    @property
    def HOST(self) -> str:
        return os.getenv('REDIS_HOST')

    @property
    def PORT(self) -> int:
        return int(os.getenv('REDIS_PORT'))

    @property
    def DB_NUMBER(self) -> int:
        return int(os.getenv('REDIS_DB_NUMBER'))

    @property
    def SSL_CERT_REQS(self) -> Literal['none', 'optional', 'required']:
        return os.getenv('REDIS_SSL_CERT_REQS')

    @property
    def SSL_CHECK_HOSTNAME(self) -> bool:
        return os.getenv('REDIS_SSL_CHECK_HOSTNAME')
