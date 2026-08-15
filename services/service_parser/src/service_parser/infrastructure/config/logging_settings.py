import os

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        json_file=os.getenv("LOGGING_SETTINGS_PATH", "/app/env/logging.json")
    )

    version: int = Field(default=1)

    disable_existing_loggers: bool = Field(default=False)

    filters: dict = Field(default_factory=dict)

    formatters: dict = Field(
        default_factory=lambda: {
            "default": {
                "format": "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
            }
        }
    )

    handlers: dict = Field(
        default_factory=lambda: {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            }
        }
    )

    loggers: dict = Field(default_factory=dict)

    root: dict = Field(
        default_factory=lambda: {"handlers": ["default"], "level": "DEBUG"}
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            JsonConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
