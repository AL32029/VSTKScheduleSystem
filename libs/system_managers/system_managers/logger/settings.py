from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
)


class BaseLoggingSettings(BaseSettings):
    version: int = Field(1)

    disable_existing_loggers: bool = Field(False)

    filters: dict = Field(default_factory=dict)

    formatters: dict = Field(
        default_factory=lambda: {
            "json": {
                "()": "system_managers.logger.MicrosecondJsonFormatter",
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%d-%m-%YT%H:%M:%S",
                "json_ensure_ascii": False,
            }
        }
    )

    handlers: dict = Field(
        default_factory=lambda: {
            "console": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout"},
            "json_console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        }
    )

    loggers: dict = Field(default_factory=dict)

    root: dict = Field(
        default_factory=lambda: {"level": "ERROR", "handlers": ["console"]}
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
