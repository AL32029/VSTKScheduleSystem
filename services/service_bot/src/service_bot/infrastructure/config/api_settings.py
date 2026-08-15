import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """Конфигурация ссылок для API"""

    model_config = SettingsConfigDict(
        env_file=os.getenv("API_SETTINGS_ENV", "/app/env/api_settings.env"),
        env_prefix="API_",
        extra="allow",
    )

    SCHEDULE_URL: str
