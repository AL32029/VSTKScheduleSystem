import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv('DATABASE_SETTINGS_PATH', '/vault/secrets/database.env'),
        env_prefix='DATABASE_',
        extra='ignore'
    )

    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    BASE: str

    @property
    def URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            host=self.HOST,
            port=self.PORT,
            username=self.USER,
            password=self.PASSWORD,
            path=self.BASE
        )
