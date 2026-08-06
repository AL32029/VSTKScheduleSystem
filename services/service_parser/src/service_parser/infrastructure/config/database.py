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

    SSL_CERT_REQS: Literal['none', 'optional', 'required'] = Field(default='required')

    SSL_CHECK_HOSTNAME: bool = Field(default=True)

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
    def URL(self) -> 'PostgresDsn':
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            host=self.HOST,
            port=self.PORT,
            path=self.BASE
        )
