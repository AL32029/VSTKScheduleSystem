import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

logger = logging.getLogger(__name__)


class DeleteMessageMiddleware(BaseMiddleware):
    """Middleware удаления текстового сообщения"""

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ):
        try:
            logger.info('Deleting the original message')
            await event.delete()
            logger.info('The original message has been successfully deleted')
        except TelegramBadRequest:
            logger.exception('Error while deleting the original message')

        await handler(event, data)
