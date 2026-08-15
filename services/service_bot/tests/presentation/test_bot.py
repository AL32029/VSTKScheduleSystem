import asyncio
import datetime
from dataclasses import asdict
from typing import cast

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram_test_framework import AsyncBotTestMixin
from dishka import AsyncContainer, Scope
from dishka.integrations.aiogram import setup_dishka
from httpx import AsyncClient

from service_bot.application.ports import UserRepository
from service_bot.domain.exceptions import (
    CabinetNotFound,
    CabinetUnsubscribeNotFound,
    GroupNotFound,
    GroupUnsubscribeNotFound,
    ScheduleForCabinetNotFound,
    ScheduleForGroupNotFound,
)
from service_bot.infrastructure.middlewares import (
    CheckMessagePanelMiddleware,
    DeleteMessageMiddleware,
    InitRequestMiddleware,
    InitUserDatabaseMiddleware,
)
from service_bot.infrastructure.repositories import (
    ScheduleItem,
    SQLAlchemyUserRepository,
)
from service_bot.infrastructure.repositories.schemas import DayScheduleItem, LessonItem
from service_bot.infrastructure.template_engine_items import (
    TemplateKeyboardRenderer,
    TemplateMessageRenderer,
)
from service_bot.presentation import UserStates, callback_router, message_router
from tests.test_contains import (
    _CABINET_DAY_SCHEDULE,
    _CABINET_ITEM,
    _CABINET_ITEMS,
    _GROUP_DAY_SCHEDULE,
    _GROUP_ITEM,
    _GROUP_ITEMS,
)


def create_app(container: AsyncContainer, bot: Bot, dispatcher: Dispatcher) -> None:
    setup_dishka(container, dispatcher)

    dispatcher.include_router(message_router)
    dispatcher.include_router(callback_router)

    dispatcher.update.middleware.register(InitRequestMiddleware())
    dispatcher.message.middleware.register(DeleteMessageMiddleware())
    dispatcher.update.middleware.register(InitUserDatabaseMiddleware())
    dispatcher.callback_query.middleware.register(CheckMessagePanelMiddleware())


class TestBot(AsyncBotTestMixin):
    @pytest.fixture(autouse=True)
    async def setup(self, test_container):
        async with test_container(scope=Scope.REQUEST) as container:
            self.client = await self.setup_client(
                setup_dispatcher_func=lambda bot, dp: create_app(container, bot, dp),
                dispatcher=Dispatcher(storage=MemoryStorage()),
            )
            yield
            await self.client.close()
            self.reset_factories()

    @pytest.fixture(autouse=True)
    async def all_groups_and_cabinets_mock(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            httpx_client = await container.get(AsyncClient)
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/groups/",
                json={
                    "success": True,
                    "data": [
                        asdict(group)
                        for group in sorted(_GROUP_ITEMS, key=lambda x: x.index)
                    ],
                },
                is_optional=True,
            )

            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/cabinets/",
                json={
                    "success": True,
                    "data": [
                        asdict(cabinet)
                        for cabinet in sorted(_CABINET_ITEMS, key=lambda x: x.index)
                    ],
                },
                is_optional=True,
            )

    async def test_start_command(self, test_container):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)

            client = self.client.create_user()

            await client.send_command("start")

            last_message = client.get_last_message()

            check_rendered_test = templater.render("main_menu", user_tg=client.user)

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
                method="GET",
                url=f"{httpx_client.base_url}/groups/{_GROUP_ITEM.number}",
                json={"success": True, "data": asdict(_GROUP_ITEM)},
            )

            client = self.client.create_user()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие страницы с добавлением группы
            await client.click_button("add_schedule_item", message=main_menu_message)

            add_schedule_item_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            user_item = await user_repo.get_by_id(client.user_id)
            add_schedule_item_text = templater.render(
                "add_schedule_item", user=user_item
            )

            assert add_schedule_item_message.text == add_schedule_item_text

            state = self._get_fsm_context(client.user)

            assert await state.get_state() == UserStates.add_schedule_item.state

            # Отправка сообщения с номером группы
            await client.send_message(_GROUP_ITEM.number)

            message = cast(Message, client.get_last_message().response)

            success_rendered_message = templater.render(
                "success_added_schedule_item", user=user_item, schedule_item=_GROUP_ITEM
            )

            assert message.text == success_rendered_message

            # Возврат в главное меню
            main_menu_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            main_menu_text = templater.render("main_menu", user_tg=client.user)

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
                method="GET",
                url=f"{httpx_client.base_url}/groups/{_GROUP_ITEM.number}",
                status_code=404,
                json={
                    "success": False,
                    "error": {
                        "code": "GROUP_NOT_FOUND",
                        "detail": f"Group with number {_GROUP_ITEM.number!r} not found",
                        "extra": {"input_number": _GROUP_ITEM.number},
                    },
                },
            )

            client = self.client.create_user()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие страницы с добавлением группы
            await client.click_button("add_schedule_item", message=main_menu_message)

            add_schedule_item_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            user_item = await user_repo.get_by_id(client.user_id)
            add_schedule_item_text = templater.render(
                "add_schedule_item", user=user_item
            )

            assert add_schedule_item_message.text == add_schedule_item_text

            state = self._get_fsm_context(client.user)

            assert await state.get_state() == UserStates.add_schedule_item.state

            # Отправка сообщения с номером группы
            await client.send_message(_GROUP_ITEM.number)

            message = cast(Message, client.get_last_message().response)

            assert message.text == f"⚠ {GroupNotFound(_GROUP_ITEM.number)!s}"

    async def test_add_cabinet_item(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/cabinets/{_CABINET_ITEM.number}",
                json={"success": True, "data": asdict(_CABINET_ITEM)},
            )

            client = self.client.create_user()

            # Предварительное создание пользователя и изменение типа профиля
            user = await user_repo.save(client.user_id)

            await user_repo.update_metadata(user, "user_type", "teacher")

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие страницы с добавлением кабинета
            await client.click_button("add_schedule_item", message=main_menu_message)

            add_schedule_item_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            user_item = await user_repo.get_by_id(client.user_id)
            add_schedule_item_text = templater.render(
                "add_schedule_item", user=user_item
            )

            assert add_schedule_item_message.text == add_schedule_item_text

            state = self._get_fsm_context(client.user)

            assert await state.get_state() == UserStates.add_schedule_item.state

            # Отправка сообщения с номером кабинета
            await client.send_message(_CABINET_ITEM.number)

            message = cast(Message, client.get_last_message().response)

            success_rendered_message = templater.render(
                "success_added_schedule_item",
                user=user_item,
                schedule_item=_CABINET_ITEM,
            )

            assert message.text == success_rendered_message

            # Возврат в главное меню
            main_menu_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            main_menu_text = templater.render("main_menu", user_tg=client.user)

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
                method="GET",
                url=f"{httpx_client.base_url}/cabinets/{_CABINET_ITEM.number}",
                status_code=404,
                json={
                    "success": False,
                    "error": {
                        "code": "CABINET_NOT_FOUND",
                        "detailt": f"Cabinet with number {_CABINET_ITEM.number!r} "
                                   f"not found",
                        "extra": {"input_number": _CABINET_ITEM.number},
                    },
                },
            )

            client = self.client.create_user()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Изменение типа профиля пользователя
            user_item = await user_repo.get_by_id(client.user_id)

            await user_repo.update_metadata(user_item, "user_type", "teacher")

            # Открытие страницы с добавлением кабинета
            await client.click_button("add_schedule_item", message=main_menu_message)

            add_schedule_item_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            add_schedule_item_text = templater.render(
                "add_schedule_item", user=user_item
            )

            assert add_schedule_item_message.text == add_schedule_item_text

            state = self._get_fsm_context(client.user)

            assert await state.get_state() == UserStates.add_schedule_item.state

            # Отправка сообщения с номером кабинета
            await client.send_message(_CABINET_ITEM.number)

            message = cast(Message, client.get_last_message().response)

            assert message.text == f"⚠ {CabinetNotFound(_CABINET_ITEM.number)!s}"

    async def test_open_main_menu(self, test_container):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo = await container.get(UserRepository)

            client = self.client.create_user()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие страницы с добавлением группы
            await client.click_button("add_schedule_item", message=main_menu_message)

            add_schedule_item_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            user_item = await user_repo.get_by_id(client.user_id)
            add_schedule_item_text = templater.render(
                "add_schedule_item", user=user_item
            )

            assert add_schedule_item_message.text == add_schedule_item_text

            state = self._get_fsm_context(client.user)

            assert await state.get_state() == UserStates.add_schedule_item.state

            # Возврат в главное меню
            await client.click_button("open_main_menu", message=main_menu_message)

            main_menu_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            main_menu_text = templater.render("main_menu", user_tg=client.user)

            assert main_menu_message.text == main_menu_text

            state = self._get_fsm_context(client.user)

            assert await state.get_state() == UserStates.main_menu.state

    async def test_update_settings(self, test_container):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)

            client = self.client.create_user()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие страницы настроек
            await client.click_button("open_settings", message=main_menu_message)

            user_settings_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            user_before = await user_repo.get_by_id(client.user_id)
            user_settings_text = templater.render("user_settings", user=user_before)

            assert user_settings_message.text == user_settings_text

            # Переключение статуса уведомлений
            await client.click_button(
                "user_settings_notifications", message=main_menu_message
            )

            user_settings_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            user_after = await user_repo.get_by_id(client.user_id)
            user_settings_text = templater.render("user_settings", user=user_after)

            assert user_settings_message.text == user_settings_text

            assert user_after.notifications_enabled == (
                not user_before.notifications_enabled
            )

            # Переключение типа профиля
            await client.click_button(
                "user_settings_profile_type", message=main_menu_message
            )

            user_settings_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            user_after = await user_repo.get_by_id(client.user_id)
            user_settings_text = templater.render("user_settings", user=user_after)

            assert user_settings_message.text == user_settings_text

            assert user_after.user_type == (
                "teacher" if user_before.user_type == "student" else "student"
            )

    async def test_get_group_day_schedule(self, test_container, httpx_mock):
        async with test_container(scope=Scope.REQUEST) as container:
            templater = await container.get(TemplateMessageRenderer)
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_GROUP_DAY_SCHEDULE.date,
                        group=ScheduleItem(**asdict(_GROUP_DAY_SCHEDULE.schedule_item)),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _GROUP_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )

            client = self.client.create_user()

            # Предварительная подписка на группу
            user = await user_repo.save(client.user_id)

            await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            day_schedule_text = templater.render(
                "day_schedule", schedule_to="group", day_schedule=_GROUP_DAY_SCHEDULE
            )

            assert day_schedule_message.text == day_schedule_text

    async def test_get_group_day_schedule_error_group_not_found(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                status_code=404,
                json={
                    "success": False,
                    "error": {
                        "code": "GROUP_NOT_FOUND",
                        "detail": f"Group with number "
                                  f"{_GROUP_DAY_SCHEDULE.schedule_item.index!r} "
                                  f"not found",
                        "extra": {
                            "input_number": _GROUP_DAY_SCHEDULE.schedule_item.index
                        },
                    },
                },
            )

            client = self.client.create_user()

            # Предварительная подписка на группу
            user = await user_repo.save(client.user_id)

            await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_error_message = self.client.capture.get_last_request().text

            assert (
                day_schedule_error_message
                == f"⚠ {GroupNotFound(_GROUP_DAY_SCHEDULE.schedule_item.index)!s}"
            )

    async def test_get_cabinet_day_schedule_error_cabinet_not_found(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/cabinet",
                match_params={
                    "cabinet_number": _CABINET_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                status_code=404,
                json={
                    "success": False,
                    "error": {
                        "code": "CABINET_NOT_FOUND",
                        "detail": f"Cabinet with number "
                                  f"{_CABINET_DAY_SCHEDULE.schedule_item.index!r} "
                                  f"not found",
                        "extra": {
                            "input_number": _CABINET_DAY_SCHEDULE.schedule_item.index
                        },
                    },
                },
            )

            client = self.client.create_user()

            # Предварительное изменение типа профиля и подписка на кабинет
            user = await user_repo.save(client.user_id)

            await user_repo.update_metadata(user, "user_type", "teacher")

            await user_repo.subscribe_cabinet(user, _CABINET_DAY_SCHEDULE.schedule_item)

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для кабинета
            await client.click_button(
                f"open_cabinet_{_CABINET_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_error_message = self.client.capture.get_last_request().text

            assert (
                day_schedule_error_message
                == f"⚠ {CabinetNotFound(_CABINET_DAY_SCHEDULE.schedule_item.index)!s}"
            )

    async def test_get_group_day_schedule_error_schedule_not_found(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                status_code=404,
                json={
                    "success": False,
                    "error": {
                        "code": "SCHEDULE_FOR_GROUP_NOT_FOUND",
                        "detail": f"For the {_GROUP_DAY_SCHEDULE.schedule_item!s} "
                                  f"group, there are no lessons "
                        f"scheduled for tomorrow (2099-12-31)",
                        "extra": {
                            "item": asdict(_GROUP_DAY_SCHEDULE.schedule_item),
                            "schedule_to": "tomorrow",
                            "schedule_date": "2099-12-31",
                        },
                    },
                },
                is_reusable=True,
            )
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "today",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_GROUP_DAY_SCHEDULE.date,
                        group=ScheduleItem(**asdict(_GROUP_DAY_SCHEDULE.schedule_item)),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _GROUP_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )

            client = self.client.create_user()

            # Предварительное подписка на группу
            user = await user_repo.save(client.user_id)

            await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            await client.click_button(
                f"schedule_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}_tomorrow",
                message=main_menu_message,
            )

            day_schedule_error_message = self.client.capture.get_last_request().text

            assert (
                day_schedule_error_message
                == f"⚠ {
                    ScheduleForGroupNotFound(
                        _GROUP_DAY_SCHEDULE.schedule_item,
                        'tomorrow',
                        datetime.date(2099, 12, 31),
                    )!s
                }"
            )

    async def test_get_cabinet_day_schedule_error_schedule_not_found(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/cabinet",
                match_params={
                    "cabinet_number": _CABINET_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                status_code=404,
                json={
                    "success": False,
                    "error": {
                        "code": "SCHEDULE_FOR_CABINET_NOT_FOUND",
                        "detail": f"For the {_CABINET_DAY_SCHEDULE.schedule_item!s} "
                                  f"cabinet, there are no lessons "
                        f"scheduled for tomorrow (2099-12-31)",
                        "extra": {
                            "item": asdict(_CABINET_DAY_SCHEDULE.schedule_item),
                            "schedule_to": "tomorrow",
                            "schedule_date": "2099-12-31",
                        },
                    },
                },
                is_reusable=True,
            )
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/cabinet",
                match_params={
                    "cabinet_number": _CABINET_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "today",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_CABINET_DAY_SCHEDULE.date,
                        cabinet=ScheduleItem(
                            **asdict(_CABINET_DAY_SCHEDULE.schedule_item)
                        ),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                group=ScheduleItem(**asdict(lesson.group)),
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _CABINET_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )

            client = self.client.create_user()

            # Предварительное изменение типа профиля и подписка на кабинет
            user = await user_repo.save(client.user_id)

            await user_repo.update_metadata(user, "user_type", "teacher")

            await user_repo.subscribe_cabinet(user, _CABINET_DAY_SCHEDULE.schedule_item)

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_cabinet_{_CABINET_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            await client.click_button(
                f"schedule_cabinet_{_CABINET_DAY_SCHEDULE.schedule_item.index}_tomorrow",
                message=main_menu_message,
            )

            day_schedule_error_message = self.client.capture.get_last_request().text

            assert (
                day_schedule_error_message
                == f"⚠ {
                    ScheduleForCabinetNotFound(
                        _CABINET_DAY_SCHEDULE.schedule_item,
                        'tomorrow',
                        datetime.date(2099, 12, 31),
                    )!s
                }"
            )

    async def test_get_group_day_schedule_switch_schedule_types(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            text_templater = await container.get(TemplateMessageRenderer)
            keyboard_templater = await container.get(TemplateKeyboardRenderer)
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_GROUP_DAY_SCHEDULE.date,
                        group=ScheduleItem(**asdict(_GROUP_DAY_SCHEDULE.schedule_item)),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _GROUP_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "today",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_GROUP_DAY_SCHEDULE.date,
                        group=ScheduleItem(**asdict(_GROUP_DAY_SCHEDULE.schedule_item)),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _GROUP_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )

            client = self.client.create_user()

            # Предварительная подписка на группу
            user = await user_repo.save(client.user_id)

            await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            last_request = self.client.capture.get_last_request()
            day_schedule_message = cast(Message, last_request.response)
            actual_keyboard = InlineKeyboardMarkup.model_validate(
                last_request.reply_markup
            )

            day_schedule_text = text_templater.render(
                "day_schedule", schedule_to="group", day_schedule=_GROUP_DAY_SCHEDULE
            )
            day_schedule_keyboard = keyboard_templater.day_schedule(
                _GROUP_DAY_SCHEDULE.schedule_item.index, "group", "tomorrow"
            )

            assert day_schedule_message.text == day_schedule_text
            assert actual_keyboard == day_schedule_keyboard

            # Переключение расписания для группы
            await client.click_button(
                f"schedule_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}_today",
                message=main_menu_message,
            )

            last_request = self.client.capture.get_last_request()
            day_schedule_message = cast(Message, last_request.response)
            actual_keyboard = InlineKeyboardMarkup.model_validate(
                last_request.reply_markup
            )

            day_schedule_text = text_templater.render(
                "day_schedule", schedule_to="group", day_schedule=_GROUP_DAY_SCHEDULE
            )
            day_schedule_keyboard = keyboard_templater.day_schedule(
                _GROUP_DAY_SCHEDULE.schedule_item.index, "group", "today"
            )

            assert day_schedule_message.text == day_schedule_text
            assert actual_keyboard == day_schedule_keyboard

    async def test_get_group_day_schedule_error_not_found(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                json={
                    "success": False,
                    "error": {
                        "code": "GROUP_NOT_FOUND",
                        "detail": f"Group with number "
                                  f"{_GROUP_DAY_SCHEDULE.schedule_item.index} "
                                  f"not found",
                        "extra": {
                            "input_number": _GROUP_DAY_SCHEDULE.schedule_item.index
                        },
                    },
                },
            )

            client = self.client.create_user()

            # Предварительная подписка на группу
            user = await user_repo.save(client.user_id)

            await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_error_message = self.client.capture.get_last_request().text

            assert (
                day_schedule_error_message
                == f"⚠ {GroupNotFound(_GROUP_DAY_SCHEDULE.schedule_item.index)!s}"
            )

    async def test_get_cabinet_day_schedule_error_not_found(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/cabinet",
                match_params={
                    "cabinet_number": _CABINET_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                json={
                    "success": False,
                    "error": {
                        "code": "CABINET_NOT_FOUND",
                        "detail": f"Cabinet with number "
                                  f"{_CABINET_DAY_SCHEDULE.schedule_item.index} "
                                  f"not found",
                        "extra": {
                            "input_number": _CABINET_DAY_SCHEDULE.schedule_item.index
                        },
                    },
                },
            )

            client = self.client.create_user()

            # Предварительное изменение типа профиля и подписка на кабинет
            user = await user_repo.save(client.user_id)

            await user_repo.update_metadata(user, "user_type", "teacher")

            await user_repo.subscribe_cabinet(user, _CABINET_DAY_SCHEDULE.schedule_item)

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для кабинета
            await client.click_button(
                f"open_cabinet_{_CABINET_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_error_message = self.client.capture.get_last_request().text

            assert (
                day_schedule_error_message
                == f"⚠ {CabinetNotFound(_CABINET_DAY_SCHEDULE.schedule_item.index)!s}"
            )

    async def test_get_group_day_schedule_with_deletion(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            text_templater = await container.get(TemplateMessageRenderer)
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_GROUP_DAY_SCHEDULE.date,
                        group=ScheduleItem(**asdict(_GROUP_DAY_SCHEDULE.schedule_item)),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _GROUP_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )

            client = self.client.create_user()

            # Предварительная подписка на группу
            user = await user_repo.save(client.user_id)

            await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

            user_repo.session.expire_all()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            day_schedule_text = text_templater.render(
                "day_schedule", schedule_to="group", day_schedule=_GROUP_DAY_SCHEDULE
            )

            assert day_schedule_message.text == day_schedule_text

            # Удаление группы
            await client.click_button(
                f"schedule_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}_delete",
                message=main_menu_message,
            )

            success_deletion_group_callback = (
                self.client.capture.get_callback_answers()[-1].text
            )

            assert (
                success_deletion_group_callback == "✔ Вы перестали отслеживать группу"
            )

    async def test_get_cabinet_day_schedule_with_deletion(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            text_templater = await container.get(TemplateMessageRenderer)
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/cabinet",
                match_params={
                    "cabinet_number": _CABINET_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_CABINET_DAY_SCHEDULE.date,
                        cabinet=ScheduleItem(
                            **asdict(_CABINET_DAY_SCHEDULE.schedule_item)
                        ),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                group=ScheduleItem(**asdict(lesson.group)),
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _CABINET_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )

            client = self.client.create_user()

            # Предварительное изменение типа профиля и подписка на кабинет
            user = await user_repo.save(client.user_id)

            await user_repo.update_metadata(user, "user_type", "teacher")

            await user_repo.subscribe_cabinet(user, _CABINET_DAY_SCHEDULE.schedule_item)

            user_repo.session.expire_all()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_cabinet_{_CABINET_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            day_schedule_text = text_templater.render(
                "day_schedule",
                schedule_to="cabinet",
                day_schedule=_CABINET_DAY_SCHEDULE,
            )

            assert day_schedule_message.text == day_schedule_text

            # Удаление кабинета
            await client.click_button(
                f"schedule_cabinet_{_CABINET_DAY_SCHEDULE.schedule_item.index}_delete",
                message=main_menu_message,
            )

            success_deletion_group_callback = (
                self.client.capture.get_callback_answers()[-1].text
            )

            assert (
                success_deletion_group_callback == "✔ Вы перестали отслеживать кабинет"
            )

    async def test_get_group_day_schedule_with_deletion_error_not_found(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            text_templater = await container.get(TemplateMessageRenderer)
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/group",
                match_params={
                    "group_number": _GROUP_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_GROUP_DAY_SCHEDULE.date,
                        group=ScheduleItem(**asdict(_GROUP_DAY_SCHEDULE.schedule_item)),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _GROUP_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )

            client = self.client.create_user()

            # Предварительная подписка на группу
            user = await user_repo.save(client.user_id)

            await user_repo.subscribe_group(user, _GROUP_DAY_SCHEDULE.schedule_item)

            user_repo.session.expire_all()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            day_schedule_text = text_templater.render(
                "day_schedule", schedule_to="group", day_schedule=_GROUP_DAY_SCHEDULE
            )

            assert day_schedule_message.text == day_schedule_text

            # Прекращение отслеживания группы
            await user_repo.unsubscribe_group(
                user, _GROUP_DAY_SCHEDULE.schedule_item.index
            )

            user_repo.session.expire_all()

            # Удаление группы
            await client.click_button(
                f"schedule_group_{_GROUP_DAY_SCHEDULE.schedule_item.index}_delete",
                message=main_menu_message,
            )

            error_callback_text = self.client.capture.get_callback_answers()[-1].text

            assert error_callback_text == f"⚠ {GroupUnsubscribeNotFound()!s}"

    async def test_get_cabinet_day_schedule_with_deletion_error_not_found(
        self, test_container, httpx_mock
    ):
        async with test_container(scope=Scope.REQUEST) as container:
            text_templater = await container.get(TemplateMessageRenderer)
            user_repo: SQLAlchemyUserRepository = await container.get(UserRepository)
            httpx_client = await container.get(AsyncClient)

            # Создание моков
            httpx_mock.add_response(
                method="GET",
                url=f"{httpx_client.base_url}/schedule/cabinet",
                match_params={
                    "cabinet_number": _CABINET_DAY_SCHEDULE.schedule_item.index,
                    "schedule_to": "tomorrow",
                },
                json={
                    "success": True,
                    "data": DayScheduleItem(
                        date=_CABINET_DAY_SCHEDULE.date,
                        cabinet=ScheduleItem(
                            **asdict(_CABINET_DAY_SCHEDULE.schedule_item)
                        ),
                        lessons=[
                            LessonItem(
                                start=lesson.start,
                                end=lesson.end,
                                group=ScheduleItem(**asdict(lesson.group)),
                                name=lesson.name,
                                cabinets=[
                                    ScheduleItem(**asdict(cabinet))
                                    for cabinet in lesson.cabinets
                                ],
                            )
                            for lesson in _CABINET_DAY_SCHEDULE.lessons
                        ],
                    ).model_dump(mode="json"),
                },
            )

            client = self.client.create_user()

            # Предварительное изменение типа профиля и подписка на кабинет
            user = await user_repo.save(client.user_id)

            await user_repo.update_metadata(user, "user_type", "teacher")

            await user_repo.subscribe_cabinet(user, _CABINET_DAY_SCHEDULE.schedule_item)

            user_repo.session.expire_all()

            # Открытие главного меню
            await client.send_command("start")

            main_menu_message = client.get_last_message().response

            # Открытие расписания для группы
            await client.click_button(
                f"open_cabinet_{_CABINET_DAY_SCHEDULE.schedule_item.index}",
                message=main_menu_message,
            )

            day_schedule_message = cast(
                Message, self.client.capture.get_last_request().response
            )

            day_schedule_text = text_templater.render(
                "day_schedule",
                schedule_to="cabinet",
                day_schedule=_CABINET_DAY_SCHEDULE,
            )

            assert day_schedule_message.text == day_schedule_text

            # Прекращение отслеживания группы
            await user_repo.unsubscribe_cabinet(
                user, _CABINET_DAY_SCHEDULE.schedule_item.index
            )

            user_repo.session.expire_all()

            # Удаление кабинета
            await client.click_button(
                f"schedule_cabinet_{_CABINET_DAY_SCHEDULE.schedule_item.index}_delete",
                message=main_menu_message,
            )

            error_callback_text = self.client.capture.get_callback_answers()[-1].text

            assert error_callback_text == f"⚠ {CabinetUnsubscribeNotFound()!s}"

    async def test_click_maintenance_free_button(self):
        client = self.client.create_user()

        # Открытие главного меню
        await client.send_command("start")

        main_menu_message = client.get_last_message().response

        await client.click_button("maintenance_free_button", message=main_menu_message)

        error_callback_text = self.client.capture.get_callback_answers()[-1].text

        assert (
            error_callback_text
            == "⚠ На данный момент данная кнопка не выполняет обработку"
        )

    def _get_fsm_context(self, user) -> FSMContext:
        return self.client.dispatcher.fsm.get_context(
            bot=self.client._bot,
            chat_id=user.id,
            user_id=user.id,
        )
