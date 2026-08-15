import os
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseSystemSettings(BaseSettings):
    """Основные настройки системы"""

    model_config = SettingsConfigDict(
        env_file=os.getenv("BASE_SETTINGS_ENV", "/app/env/base_settings.env"),
        env_prefix="SYSTEM_",
        extra="allow",
    )

    TIMEZONE: str = Field(default="Europe/Minsk")

    @property
    def TZ(self) -> ZoneInfo:
        return ZoneInfo(self.TIMEZONE)
