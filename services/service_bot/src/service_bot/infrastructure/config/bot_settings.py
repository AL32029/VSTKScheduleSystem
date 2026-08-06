import os

from pydantic_settings import BaseSettings, SettingsConfigDict


# TODO: Реализовать конфигурацию для продакшена
class BotSettings(BaseSettings):
    """Конфигурация базы данных"""
    model_config = SettingsConfigDict(
        env_file=os.getenv('BOT_SETTINGS_ENV', '/vault/secrets/bot_settings.env'),
        env_prefix='BOT_',
        extra='allow'
    )

    TOKEN: str
