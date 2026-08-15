from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings


class BaseSystemSettings(BaseSettings):
    SYSTEM_MODE: Literal["dev", "prod"] = Field(default="prod")

    TZ: str = Field(alias="TIMEZONE", default="Europe/Minsk")

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.TZ)
