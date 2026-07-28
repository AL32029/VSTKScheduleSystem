import os

from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv('REDIS_SETTINGS_PATH', '/vault/secrets/redis.env'),
        env_prefix='REDIS_',
        extra='ignore'
    )

    HOST: str
    PORT: int
    USER: str | None
    PASSWORD: str | None
    DB_NUMBER: int

    @property
    def URL(self) -> RedisDsn:
        return RedisDsn.build(
            scheme='redis',
            host=self.HOST,
            port=self.PORT,
            username=self.USER,
            password=self.PASSWORD,
            path=str(self.DB_NUMBER)
        )
