import asyncio
import locale
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka
from redis.asyncio import Redis

from service_bot.infrastructure.di.container import get_dishka_container
from service_bot.infrastructure.middlewares import (
    CheckMessagePanelMiddleware,
    DeleteMessageMiddleware,
    InitUserDatabaseMiddleware,
)
from service_bot.presentation import callback_router, main_menu_router

logging.basicConfig(level=logging.DEBUG)

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    logging.debug('Установлена русская локаль даты')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'russian')
        logging.debug('Установлена русская локаль даты')
    except locale.Error:
        logging.debug('Русская локаль не найдена, используется стандартная"')
        raise

async def create_app(container: 'AsyncContainer | None' = None) -> 'tuple[Bot, Dispatcher]':
    cont = container or get_dishka_container()

    redis_provider: Redis = await cont.get(Redis)
    bot: Bot = await cont.get(Bot)

    dp = Dispatcher(storage=RedisStorage(redis_provider, state_ttl=1209600, data_ttl=1209600))

    setup_dishka(cont, dp)

    dp.include_router(main_menu_router)
    dp.include_router(callback_router)

    dp.message.middleware.register(DeleteMessageMiddleware())
    dp.update.middleware.register(InitUserDatabaseMiddleware())
    dp.callback_query.middleware.register(CheckMessagePanelMiddleware())

    return bot, dp


async def main():
    bot, dp = await create_app()

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
