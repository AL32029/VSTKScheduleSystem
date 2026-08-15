import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DevDatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_", extra="forbid")

    HOST: str
    PORT: int

    USER: str
    PASSWORD: str | None = Field(None)

    BASE: str


class ProdDatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("DATABASE_SETTINGS_ENV", "/vault/secrets/database.env"),
        env_prefix="DATABASE_",
        extra="forbid",
    )

    HOST: str
    PORT: int

    BASE: str

    SSL_CERT_REQS: Literal["none", "optional", "required"] = Field("required")

    SSL_CERT_FILE: str = Field(default="/vault/secrets/database-tls.crt")
    SSL_KEY_FILE: str = Field(default="/vault/secrets/database-tls.key")
    SSL_CA_CERT_FILE: str = Field(default="/vault/secrets/database-tls.ca")

    SSL_CHECK_HOSTNAME: bool = Field(True)


class DatabaseSettings:
    def __init__(self, mode: Literal["dev", "prod"] = "dev"):
        self.mode = mode
        self.dev: "DevDatabaseSettings" = DevDatabaseSettings()
        self.prod: "ProdDatabaseSettings" = ProdDatabaseSettings()

    @property
    def config(self):
        return self.dev if self.mode == "dev" else self.prod
