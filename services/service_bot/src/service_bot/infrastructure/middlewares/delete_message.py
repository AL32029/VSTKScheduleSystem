from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message


class DeleteMessageMiddleware(BaseMiddleware):
    """Middleware удаления текстового сообщения"""
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ):
        try:
            await event.delete()
        except:
            pass

        await handler(event, data)
