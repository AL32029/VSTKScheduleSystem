import logging
import textwrap
import time
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Update

from service_bot.domain.context_vars import (
    message_id_var,
    request_id_var,
    update_id_var,
    user_id_var,
)

logger = logging.getLogger(__name__)


class InitRequestMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ):
        if not event.message and not event.callback_query:
            return None

        instance = event.message or event.callback_query

        if instance.from_user.is_bot:
            return None

        request_id_var.set(str(uuid4()))
        update_id_var.set(event.update_id)
        user_id_var.set(instance.from_user.id)
        start = time.perf_counter()

        if isinstance(instance, CallbackQuery):
            request_type = f"Callback {instance.data}"
            chat_id = (
                instance.message.chat.id
                if instance.message and instance.message.chat
                else None
            )
            message_id_var.set(instance.message.message_id)
        else:
            text_preview = (
                textwrap.shorten(instance.text, width=48, placeholder="...")
                if instance.text
                else ""
            )
            request_type = f"Message {text_preview}"
            chat_id = instance.chat.id if instance.chat else None
            message_id_var.set(instance.message_id)

        logger.info(
            "%s received",
            request_type,
            extra={
                "request_type": request_type,
                "chat_id": chat_id,
            },
        )

        response = await handler(event, data)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s completed",
            request_type,
            extra={
                "request_type": request_type,
                "duration_ms": duration_ms,
            },
        )
        return response
