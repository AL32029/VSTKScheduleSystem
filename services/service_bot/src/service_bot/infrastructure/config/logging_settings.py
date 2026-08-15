import os

from pydantic_settings import (
    SettingsConfigDict,
)
from system_managers import BaseLoggingSettings


class LoggingSettings(BaseLoggingSettings):
    model_config = SettingsConfigDict(
        json_file=os.getenv("LOGGING_SETTINGS_PATH", "/app/env/logging.json"),
    )
