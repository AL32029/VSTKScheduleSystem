from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from service_bot.domain.entities import User


class CheckMessagePanelMiddleware(BaseMiddleware):
    """Middleware проверки ID сообщения с ID панелью"""
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: dict[str, Any]
    ):
        user: User = data['user']

        if user.message_panel_id != event.message.message_id:
            await event.message.edit_reply_markup(reply_markup=None)

            return await event.answer('⚠ Взаимодействие с данным сообщением невозможно')

        await handler(event, data)
