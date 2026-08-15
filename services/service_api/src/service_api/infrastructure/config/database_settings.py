import os
from typing import Literal

from pydantic_settings import SettingsConfigDict
from system_managers import BaseDevDatabaseSettings, BaseProdDatabaseSettings


class DevDatabaseSettings(BaseDevDatabaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_", extra="forbid")


class ProdDatabaseSettings(BaseProdDatabaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("DATABASE_SETTINGS_ENV", "/vault/secrets/database.env"),
        env_prefix="DATABASE_",
        extra="forbid",
    )


class DatabaseSettings:
    def __init__(self, mode: Literal["dev", "prod"] = "dev"):
        self.mode = mode
        self.dev: DevDatabaseSettings = DevDatabaseSettings()
        self.prod: ProdDatabaseSettings = ProdDatabaseSettings()

    @property
    def config(self):
        return self.dev if self.mode == "dev" else self.prod
