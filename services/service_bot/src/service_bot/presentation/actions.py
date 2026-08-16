import asyncio
import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from service_bot.domain.context_vars import (
    message_id_var,
    request_id_var,
    update_id_var,
    user_id_var,
)

logger = logging.getLogger(__name__)


async def delete_message_with_delay(
    message: Message,
    request_id,
    update_id,
    user_id,
    message_id,
    delay: float = 7.5,
):
    """Удаление сообщения спустя КД"""
    request_id_var.set(request_id)
    update_id_var.set(update_id)
    user_id_var.set(user_id)
    message_id_var.set(message_id)

    logger.info(
        "The task of deleting the message with ID %s is scheduled "
        "for %s seconds from now",
        message.message_id,
        delay,
    )
    await asyncio.sleep(delay)
    try:
        logger.info("Deleting a message with ID %s", message.message_id)
        await message.delete()
        logger.info("The message with ID %s has been deleted", message.message_id)
    except TelegramBadRequest as e:
        logger.warning(
            "Error while deleting message with ID %s - %s",
            message.message_id,
            e.message,
        )
