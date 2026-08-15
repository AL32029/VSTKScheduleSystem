import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update
from dishka import AsyncContainer

from service_bot.application.ports import UserRepository
from service_bot.domain.exceptions import UserNotFound

logger = logging.getLogger(__name__)


class InitUserDatabaseMiddleware(BaseMiddleware):
    """Middleware инициализации пользователя в базе данных"""

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ):
        instance = event.message or event.callback_query

        container: AsyncContainer | None = data.get("dishka_container")
        if container is None:
            raise RuntimeError("Dishka container not found in data")

        user_repository = await container.get(UserRepository)

        if user_repository is None:
            return None

        try:
            logger.info("Initialize user from database")
            user = await user_repository.get_by_id(instance.from_user.id)
            logger.info("User was found in database")
        except UserNotFound:
            logger.info("User not found in database")
            logger.info("Registration user in database")
            user = await user_repository.save(instance.from_user.id)
            logger.info("User was registered successfully")

        data["user"] = user

        old_metadata = user.metadata.copy()

        result = await handler(event, data)

        user = data["user"]

        if user.metadata != old_metadata:
            for k, v in user.metadata.items():
                if old_metadata[k] != v:
                    await user_repository.update_metadata(user, k, v)

        return result
