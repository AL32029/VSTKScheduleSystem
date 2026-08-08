import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from service_bot.domain.entities import User

logger = logging.getLogger(__name__)


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
            logger.warning('The message is not a control panel; the keyboard is being removed')
            try:
                await event.message.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest:
                logger.exception('Error while deleting the keyboard')
            else:
                logger.info('The keyboard has been successfully removed')

            return await event.answer('⚠ Взаимодействие с данным сообщением невозможно')

        await handler(event, data)
