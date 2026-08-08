import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Конфигурация бота"""
    model_config = SettingsConfigDict(
        env_file=os.getenv('BOT_SETTINGS_ENV', '/vault/secrets/bot_settings.env'),
        env_prefix='BOT_',
        extra='ignore'
    )

    TOKEN: str
