import asyncio
from dataclasses import asdict
from typing import cast

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_test_framework import AsyncBotTestMixin
from dishka import AsyncContainer, Scope
from dishka.integrations.aiogram import setup_dishka
from httpx import AsyncClient

from service_bot.application.ports import UserRepository
from service_bot.domain.exceptions import GroupNotFound, CabinetNotFound
from service_bot.infrastructure.repositories import SQLAlchemyUserRepository, ScheduleItem
from service_bot.infrastructure.repositories.schemas import DayScheduleItem, LessonItem
from service_bot.infrastructure.template_engine_items import TemplateMessageRenderer
from service_bot.presentation import UserStates
from src.service_bot.infrastructure.middlewares import (
    CheckMessagePanelMiddleware,
    DeleteMessageMiddleware,
    InitRequestMiddleware,
    InitUserDatabaseMiddleware,
)
from src.service_bot.presentation import callback_router, message_router
from tests.test_contains import _CABINET_ITEM, _CABINET_ITEMS, _GROUP_ITEM, _GROUP_ITEMS, _GROUP_DAY_SCHEDULE


def create_app(container: AsyncContainer, bot: Bot, dispatcher: Dispatcher) -> None:
    setup_dishka(container, dispatcher)

    dispatcher.include_router(message_router)
    dispatcher.include_router(callback_router)

    dispatcher.update.middleware.register(InitRequestMiddleware())
    dispatcher.message.middleware.register(DeleteMessageMiddleware())
    dispatcher.update.middleware.register(InitUserDatabaseMiddleware())
    dispatcher.callback_query.middleware.register(CheckMessagePanelMiddleware())


class TestBot(AsyncBotTestMixin):
    """
    Класс-наследник AsyncBotTestMixin.
    В нём мы определяем фикстуру setup, которая инициализирует клиента.
    """

    @pytest.fixture(autouse=True)
    async def setup(self, test_container):
        async with test_container(scope=Scope.REQUEST) as container:
            self.client = await self.setup_client(
                setup_dispatcher_func=lambda bot, dp: create_app(container, bot, dp),
                dispatcher=Dispatcher(storage=MemoryStorage())
            )
            yield
            await self.client.close()
            self.reset_factories()

    async def test_start_command(self, test_container):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)

        client = self.client.create_user()

        await client.send_command('start')

        last_message = client.get_last_message()

        check_rendered_test = templater.render('main_menu', user_tg=client.user)

        assert last_message.text == check_rendered_test

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.main_menu.state

    async def test_add_group_item(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

        # Создание моков
        httpx_mock.add_response(
            method='GET',
            url=f'{httpx_client.base_url}/groups/',
            json=[asdict(group) for group in sorted(_GROUP_ITEMS, key=lambda x: x.index)]
        )

        httpx_mock.add_response(
            method='GET',
            url=f'{httpx_client.base_url}/groups/{_GROUP_ITEM.number}',
            json=asdict(_GROUP_ITEM)
        )

        client = self.client.create_user()

        # Открытие главного меню
        await client.send_command('start')

        main_menu_message = client.get_last_message().response

        # Открытие страницы с добавлением группы
        await client.click_button('add_schedule_item', message=main_menu_message)

        add_schedule_item_message = cast(Message, self.client.capture.get_last_request().response)

        user_item = await user_repo.get_by_id(client.user_id)
        add_schedule_item_text = templater.render('add_schedule_item', user=user_item)

        assert add_schedule_item_message.text == add_schedule_item_text

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.add_schedule_item.state

        # Отправка сообщения с номером группы
        await client.send_message(_GROUP_ITEM.number)

        message = cast(Message, client.get_last_message().response)

        success_rendered_message = templater.render('success_added_schedule_item', user=user_item,
                                                    schedule_item=_GROUP_ITEM)

        assert message.text == success_rendered_message

        # Возврат в главное меню
        main_menu_message = cast(Message, self.client.capture.get_last_request().response)

        main_menu_text = templater.render('main_menu', user_tg=client.user)

        assert main_menu_message.text == main_menu_text

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.main_menu.state

    async def test_add_group_item_error_not_found(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

        # Создание моков
        httpx_mock.add_response(
            method='GET',
            url=f'{httpx_client.base_url}/groups/{_GROUP_ITEM.number}',
            status_code=404,
            content=f'Group with number {_GROUP_ITEM.number!r} not found'
        )

        client = self.client.create_user()

        # Открытие главного меню
        await client.send_command('start')

        main_menu_message = client.get_last_message().response

        # Открытие страницы с добавлением группы
        await client.click_button('add_schedule_item', message=main_menu_message)

        add_schedule_item_message = cast(Message, self.client.capture.get_last_request().response)

        user_item = await user_repo.get_by_id(client.user_id)
        add_schedule_item_text = templater.render('add_schedule_item', user=user_item)

        assert add_schedule_item_message.text == add_schedule_item_text

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.add_schedule_item.state

        # Отправка сообщения с номером группы
        await client.send_message(_GROUP_ITEM.number)

        message = cast(Message, client.get_last_message().response)

        assert message.text == f'⚠ {GroupNotFound(_GROUP_ITEM.number)!s}'

    async def test_add_cabinet_item(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

        # Создание моков
        httpx_mock.add_response(
            method='GET',
            url=f'{httpx_client.base_url}/cabinets/',
            json=[asdict(cabinet) for cabinet in sorted(_CABINET_ITEMS, key=lambda x: x.index)]
        )

        httpx_mock.add_response(
            method='GET',
            url=f'{httpx_client.base_url}/cabinets/{_CABINET_ITEM.number}',
            json=asdict(_CABINET_ITEM)
        )

        client = self.client.create_user()

        # Предварительное создание пользователя и изменение типа профиля
        user = await user_repo.save(client.user_id)

        await user_repo.update_metadata(user, 'user_type', 'teacher')

        # Открытие главного меню
        await client.send_command('start')

        main_menu_message = client.get_last_message().response

        # Открытие страницы с добавлением кабинета
        await client.click_button('add_schedule_item', message=main_menu_message)

        add_schedule_item_message = cast(Message, self.client.capture.get_last_request().response)

        user_item = await user_repo.get_by_id(client.user_id)
        add_schedule_item_text = templater.render('add_schedule_item', user=user_item)

        assert add_schedule_item_message.text == add_schedule_item_text

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.add_schedule_item.state

        # Отправка сообщения с номером кабинета
        await client.send_message(_CABINET_ITEM.number)

        message = cast(Message, client.get_last_message().response)

        success_rendered_message = templater.render('success_added_schedule_item', user=user_item,
                                                    schedule_item=_CABINET_ITEM)

        assert message.text == success_rendered_message

        # Возврат в главное меню
        main_menu_message = cast(Message, self.client.capture.get_last_request().response)

        main_menu_text = templater.render('main_menu', user_tg=client.user)

        # Сон для проработки удаления сообщения (7.5сек)
        await asyncio.sleep(7.5)

        assert main_menu_message.text == main_menu_text

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.main_menu.state

    async def test_add_cabinet_item_error_not_found(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

        # Создание моков
        httpx_mock.add_response(
            method='GET',
            url=f'{httpx_client.base_url}/cabinets/{_CABINET_ITEM.number}',
            status_code=404,
            content=f'Cabinet with number {_CABINET_ITEM.number!r} not found'
        )

        client = self.client.create_user()

        # Открытие главного меню
        await client.send_command('start')

        main_menu_message = client.get_last_message().response

        # Изменение типа профиля пользователя
        user_item = await user_repo.get_by_id(client.user_id)

        await user_repo.update_metadata(user_item, 'user_type', 'teacher')

        # Открытие страницы с добавлением кабинета
        await client.click_button('add_schedule_item', message=main_menu_message)

        add_schedule_item_message = cast(Message, self.client.capture.get_last_request().response)

        add_schedule_item_text = templater.render('add_schedule_item', user=user_item)

        assert add_schedule_item_message.text == add_schedule_item_text

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.add_schedule_item.state

        # Отправка сообщения с номером кабинета
        await client.send_message(_CABINET_ITEM.number)

        message = cast(Message, client.get_last_message().response)

        assert message.text == f'⚠ {CabinetNotFound(_CABINET_ITEM.number)!s}'

    async def test_open_main_menu(self, test_container):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo = await container.get(UserRepository)

        client = self.client.create_user()

        # Открытие главного меню
        await client.send_command('start')

        main_menu_message = client.get_last_message().response

        # Открытие страницы с добавлением группы
        await client.click_button('add_schedule_item', message=main_menu_message)

        add_schedule_item_message = cast(Message, self.client.capture.get_last_request().response)

        user_item = await user_repo.get_by_id(client.user_id)
        add_schedule_item_text = templater.render('add_schedule_item', user=user_item)

        assert add_schedule_item_message.text == add_schedule_item_text

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.add_schedule_item.state

        # Возврат в главное меню
        await client.click_button('open_main_menu', message=main_menu_message)

        main_menu_message = cast(Message, self.client.capture.get_last_request().response)

        main_menu_text = templater.render('main_menu', user_tg=client.user)

        assert main_menu_message.text == main_menu_text

        state = self._get_fsm_context(client.user)

        assert await state.get_state() == UserStates.main_menu.state

    async def test_update_settings(self, test_container):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo: 'SQLAlchemyUserRepository' = await container.get(UserRepository)

        client = self.client.create_user()

        # Открытие главного меню
        await client.send_command('start')

        main_menu_message = client.get_last_message().response

        # Открытие страницы настроек
        await client.click_button('open_settings', message=main_menu_message)

        user_settings_message = cast(Message, self.client.capture.get_last_request().response)

        user_before = await user_repo.get_by_id(client.user_id)
        user_settings_text = templater.render('user_settings', user=user_before)

        assert user_settings_message.text == user_settings_text

        # Переключение статуса уведомлений
        await client.click_button('user_settings_notifications', message=main_menu_message)

        user_settings_message = cast(Message, self.client.capture.get_last_request().response)

        user_after = await user_repo.get_by_id(client.user_id)
        user_settings_text = templater.render('user_settings', user=user_after)

        assert user_settings_message.text == user_settings_text

        assert user_after.notifications_enabled == (not user_before.notifications_enabled)

        # Переключение типа профиля
        await client.click_button('user_settings_profile_type', message=main_menu_message)

        user_settings_message = cast(Message, self.client.capture.get_last_request().response)

        user_after = await user_repo.get_by_id(client.user_id)
        user_settings_text = templater.render('user_settings', user=user_after)

        assert user_settings_message.text == user_settings_text

        assert user_after.user_type == ('teacher' if user_before.user_type == 'student' else 'student')

    async def test_get_group_day_schedule(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo: 'SQLAlchemyUserRepository' = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

        # Создание моков
        httpx_mock.add_response(
            method='GET',
            url=f'{httpx_client.base_url}/schedule/group',
            match_params={
                'group_number': _GROUP_DAY_SCHEDULE.schedule_item.index,
                'schedule_to': 'tomorrow'
            },
            json=DayScheduleItem(
                date=_GROUP_DAY_SCHEDULE.date,
                group=ScheduleItem(**asdict(_GROUP_DAY_SCHEDULE.schedule_item)),
                lessons=[
                    LessonItem(start=lesson.start, end=lesson.end, name=lesson.name,
                               cabinets=[ScheduleItem(**asdict(cabinet)) for cabinet in lesson.cabinets])
                    for lesson in _GROUP_DAY_SCHEDULE.lessons
                ]
            ).model_dump(mode='json')
        )

        client = self.client.create_user()

        # Предварительная подписка на группу
        user = await user_repo.save(client.user_id)

        await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

        # Открытие главного меню
        await client.send_command('start')

        main_menu_message = client.get_last_message().response

        # Открытие расписания для группы
        await client.click_button(f'open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}', message=main_menu_message)

        day_schedule_message = cast(Message, self.client.capture.get_last_request().response)

        user_settings_text = templater.render('day_schedule', schedule_to='group', day_schedule=_GROUP_DAY_SCHEDULE)

        assert day_schedule_message.text == user_settings_text

    async def test_get_group_day_schedule_error_group_not_found(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo: 'SQLAlchemyUserRepository' = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

        # Создание моков
        httpx_mock.add_response(
            method='GET',
            url=f'{httpx_client.base_url}/schedule/group',
            match_params={
                'group_number': _GROUP_DAY_SCHEDULE.schedule_item.index,
                'schedule_to': 'tomorrow'
            },
            status_code=404,
            content=f'Group with number {_GROUP_DAY_SCHEDULE.schedule_item.index!r} not found'
        )

        client = self.client.create_user()

        # Предварительная подписка на группу
        user = await user_repo.save(client.user_id)

        await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

        # Открытие главного меню
        await client.send_command('start')

        main_menu_message = client.get_last_message().response

        # Открытие расписания для группы
        await client.click_button(f'open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}', message=main_menu_message)

        day_schedule_error_message = self.client.capture.get_last_request().text

        assert day_schedule_error_message == f'⚠ {GroupNotFound(_GROUP_DAY_SCHEDULE.schedule_item.index)!s}'

    def _get_fsm_context(self, user) -> FSMContext:
        return self.client.dispatcher.fsm.get_context(
            bot=self.client._bot,
            chat_id=user.id,
            user_id=user.id,
        )
