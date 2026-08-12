from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='BASE_',
        extra='allow'
    )

    TZ: str = Field(alias='TIMEZONE', default='Europe/Minsk')

    @property
    def TIMEZONE(self) -> ZoneInfo:
        return ZoneInfo(self.TZ)
