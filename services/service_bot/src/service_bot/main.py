import asyncio.exceptions
import functools
import logging.config
from asyncio import Task
from pathlib import Path
from typing import cast

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka
from redis.asyncio import Redis
from watchfiles import Change, awatch

from service_bot.infrastructure.config import LoggingSettings
from service_bot.infrastructure.di.container import get_dishka_container
from service_bot.infrastructure.managers import (
    DatabaseEngineManager,
    RedisClientManager,
)
from service_bot.infrastructure.middlewares import (
    CheckMessagePanelMiddleware,
    DeleteMessageMiddleware,
    InitRequestMiddleware,
    InitUserDatabaseMiddleware,
)
from service_bot.presentation import callback_router, message_router

logging.config.dictConfig(LoggingSettings().model_dump(mode='json'))

logger = logging.getLogger('service_bot')


async def watch_loop(db_manager: 'DatabaseEngineManager', redis_client: 'RedisClientManager'):
    logger.info('WatchLoop has been initialized')

    db_paths = {db_manager.settings.SSL_CERT_FILE, db_manager.settings.SSL_KEY_FILE,
                db_manager.settings.SSL_CA_CERT_FILE}
    redis_paths = {redis_client.settings.SSL_CERT_FILE, redis_client.settings.SSL_KEY_FILE,
                   redis_client.settings.SSL_CA_CERT_FILE}
    all_paths = db_paths | redis_paths

    watch_dirs = {str(Path(p).parent) for p in all_paths}

    def relevant_change(change: Change, path: str) -> bool:
        return path in all_paths

    try:
        async for changes in awatch(*watch_dirs, watch_filter=relevant_change, debounce=2000):
            logger.info('Changes have been detected in the monitored files')
            certs_changes = {p for _, p in changes}

            tasks_run = []
            if db_paths & certs_changes:
                logger.info('Running the database credential rotation task')
                tasks_run.append(asyncio.create_task(db_manager.rotate()))
                logger.info('The database credential rotation task has been launched')
            if redis_paths & certs_changes:
                logger.info('Running the redis credential rotation task')
                tasks_run.append(asyncio.create_task(redis_client.rotate()))
                logger.info('The redis credential rotation task has been launched')

            await asyncio.gather(*tasks_run, return_exceptions=True)
    except Exception:
        logger.exception('An error occurred during the WatchLoop change tracking')

    logger.info('WatchLoop has stopped working')


async def on_startup(dispatcher: Dispatcher, container: AsyncContainer) -> None:
    db_manager = await container.get(DatabaseEngineManager)
    redis_client = await container.get(RedisClientManager)

    await db_manager.get_engine()
    await redis_client.get_client()

    dispatcher['watch_loop_task'] = asyncio.create_task(watch_loop(db_manager, redis_client))


async def on_shutdown(dispatcher: Dispatcher, container: AsyncContainer) -> None:
    watch_loop_task: Task | None = cast('Task | None', dispatcher.get('watch_loop_task'))

    db_manager = await container.get(DatabaseEngineManager)
    redis_client = await container.get(RedisClientManager)

    if watch_loop_task is not None:
        watch_loop_task.cancel()

    await asyncio.gather(
        *(t for t in (watch_loop_task,) if t is not None),
        db_manager.dispose(),
        redis_client.close(),
        return_exceptions=True,
    )


async def create_app(container: 'AsyncContainer | None' = None) -> 'tuple[Bot, Dispatcher]':
    cont = container or get_dishka_container()

    redis_provider: Redis = await cont.get(Redis)
    bot: Bot = await cont.get(Bot)

    dp = Dispatcher(storage=RedisStorage(redis_provider, state_ttl=1209600, data_ttl=1209600))

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


if __name__ == '__main__':
    asyncio.run(main())
