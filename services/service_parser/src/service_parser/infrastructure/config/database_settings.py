import os
from typing import Literal

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv('DATABASE_SETTINGS_ENV', '/vault/secrets/database.env'),
        env_prefix='DATABASE_',
        extra='ignore'
    )

    SSL_CERT_FILE: str = Field(default='/vault/secrets/database-tls.crt')
    SSL_KEY_FILE: str = Field(default='/vault/secrets/database-tls.key')
    SSL_CA_CERT_FILE: str = Field(default='/vault/secrets/database-tls.ca')

    @property
    def HOST(self) -> str:
        return os.getenv('DATABASE_HOST')

    @property
    def PORT(self) -> int:
        return int(os.getenv('DATABASE_PORT'))

    @property
    def BASE(self) -> str:
        return os.getenv('DATABASE_BASE')

    @property
    def SSL_CERT_REQS(self) -> Literal['none', 'optional', 'required']:
        return os.getenv('DATABASE_SSL_CERT_REQS')

    @property
    def SSL_CHECK_HOSTNAME(self) -> bool:
        return os.getenv('DATABASE_SSL_CHECK_HOSTNAME')

    @property
    def URL(self) -> 'PostgresDsn':
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            host=self.HOST,
            port=self.PORT,
            path=self.BASE
        )
