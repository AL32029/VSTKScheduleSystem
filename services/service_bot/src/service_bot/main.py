import asyncio.exceptions
import functools
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka
from redis.asyncio import Redis
from system_managers import DatabaseEngineManager, RedisClientManager, WatchFilesManager

from service_bot.infrastructure.config import LoggingSettings, system_settings
from service_bot.infrastructure.di.container import get_dishka_container
from service_bot.infrastructure.middlewares import (
    CheckMessagePanelMiddleware,
    DeleteMessageMiddleware,
    InitRequestMiddleware,
    InitUserDatabaseMiddleware,
)
from service_bot.presentation import callback_router, message_router

logging.config.dictConfig(LoggingSettings().model_dump(mode="json"))

logger = logging.getLogger("service_bot")


async def on_startup(dispatcher: Dispatcher, container: AsyncContainer) -> None:
    db_manager: DatabaseEngineManager = await container.get(DatabaseEngineManager)
    redis_client: RedisClientManager = await container.get(RedisClientManager)

    await db_manager.rotate()
    await redis_client.rotate()

    if system_settings.SYSTEM_MODE == "prod":
        watch_files_manager: WatchFilesManager = await container.get(WatchFilesManager)

        try:
            dispatcher["watch_files_manager"] = watch_files_manager
            dispatcher["watch_loop_task"] = asyncio.create_task(
                watch_files_manager.watch(db_manager, redis_client)
            )
            logger.info("Watchfiles task started")
        except Exception:
            logger.exception("Failed to start watchfiles task")


async def on_shutdown(dispatcher: Dispatcher, container: AsyncContainer) -> None:
    watch_files_task = dispatcher.get("watch_loop_task")

    if system_settings.SYSTEM_MODE == "prod" and watch_files_task is not None:
        db_manager: DatabaseEngineManager = await container.get(DatabaseEngineManager)
        redis_client: RedisClientManager = await container.get(RedisClientManager)

        if watch_files_task and not watch_files_task.done():
            watch_files_task.cancel()
            try:
                await watch_files_task
            except asyncio.CancelledError:
                logger.info("Watchfiles task cancelled")
            except Exception:
                logger.exception("Watchfiles task failed during shutdown")

        if db_manager is not None:
            try:
                await db_manager.dispose()
            except Exception:
                logger.exception("Error disposing database engine")

        if redis_client is not None:
            try:
                await redis_client.close()
            except Exception:
                logger.exception("Error closing Redis client")


async def create_app(
    container: "AsyncContainer | None" = None,
) -> "tuple[Bot, Dispatcher]":
    cont = container or get_dishka_container()

    redis_provider: Redis = await cont.get(Redis)
    bot: Bot = await cont.get(Bot)

    dp = Dispatcher(
        storage=RedisStorage(redis_provider, state_ttl=1209600, data_ttl=1209600),
    )

    setup_dishka(cont, dp)

    dp.include_router(message_router)
    dp.include_router(callback_router)

    dp.update.middleware.register(InitRequestMiddleware())
    dp.message.middleware.register(DeleteMessageMiddleware())
    dp.update.middleware.register(InitUserDatabaseMiddleware())
    dp.callback_query.middleware.register(CheckMessagePanelMiddleware())

    dp.startup.register(functools.partial(on_startup, container=cont))
    dp.shutdown.register(functools.partial(on_shutdown, container=cont))

    return bot, dp


async def main():
    bot, dp = await create_app()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
