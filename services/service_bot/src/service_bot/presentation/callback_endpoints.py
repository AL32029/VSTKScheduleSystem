import datetime
import logging
from typing import Literal
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.exceptions import AiogramError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from service_bot.application.services import (
    GetAllCabinetsUseCase,
    GetAllGroupsUseCase,
    GetDayScheduleUseCase,
    UnsubscribeCabinetUseCase,
    UnsubscribeGroupUseCase,
)
from service_bot.domain.entities import User
from service_bot.domain.exceptions import (
    CabinetUnsubscribeNotFoundError,
    GroupUnsubscribeNotFoundError,
    ScheduleDateNotFoundError,
    ScheduleForCabinetNotFoundError,
    ScheduleForGroupNotFoundError,
)
from service_bot.infrastructure.template_engine_items import (
    TemplateKeyboardRenderer,
    TemplateMessageRenderer,
)

from .callback_patterns import (
    DAY_SCHEDULE_PANEL_COMPILE,
    OPEN_DAY_SCHEDULE_COMPILE,
    USER_SETTINGS_COMPILE,
)
from .user_states import UserStates

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "open_main_menu")
@inject
async def callback_open_main_menu(
    callback: CallbackQuery,
    state: FSMContext,
    user: "User",
    message_templater: FromDishka["TemplateMessageRenderer"],
    keyboard_templater: FromDishka["TemplateKeyboardRenderer"],
    all_groups_use_case: FromDishka["GetAllGroupsUseCase"],
    all_cabinets_use_case: FromDishka["GetAllCabinetsUseCase"],
):
    """Callback обработчик открытия главного меню"""
    is_student = user.user_type == "student"

    schedule_items = (
        await all_groups_use_case.execute()
        if is_student and user.group_subscribes
        else await all_cabinets_use_case.execute()
        if not is_student and user.cabinet_subscribes
        else []
    )

    rendered_text = message_templater.render("main_menu", user_tg=callback.from_user)
    rendered_keyboard = keyboard_templater.main_menu(user, schedule_items)

    user_state = UserStates.main_menu

    logger.info("Changing the user status to %s", user_state.state)
    await state.set_state(user_state)
    logger.info("The user status has been changed to %s", user_state.state)

    logger.info("Changing the message to the main menu")
    await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)
    logger.info("The message has been changed to the main menu")


@router.callback_query(F.data == "add_schedule_item")
@inject
async def callback_add_schedule_item(
    callback: CallbackQuery,
    state: FSMContext,
    user: "User",
    message_templater: FromDishka["TemplateMessageRenderer"],
    keyboard_templater: FromDishka["TemplateKeyboardRenderer"],
):
    """Callback обработчик открытия диалога добавления группы/кабинета"""
    rendered_text = message_templater.render("add_schedule_item", user=user)
    rendered_keyboard = keyboard_templater.to_main_menu()

    user_state = UserStates.add_schedule_item

    logger.info("Changing the user status to %s", user_state.state)
    await state.set_state(user_state)
    logger.info("The user status has been changed to %s", user_state.state)

    logger.info("Changing the message to the add schedule item page")
    await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)
    logger.info("The message has been changed to the add schedule item page")


@router.callback_query(F.data == "open_settings")
@inject
async def callback_open_settings(
    callback: CallbackQuery,
    user: "User",
    message_templater: FromDishka["TemplateMessageRenderer"],
    keyboard_templater: FromDishka["TemplateKeyboardRenderer"],
):
    """Callback обработчик открытия панели настроек"""
    rendered_text = message_templater.render("user_settings", user=user)
    rendered_keyboard = keyboard_templater.user_settings(user)

    logger.info("Changing the message to the settings page")
    await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)
    logger.info("The message has been changed to the settings page")


@router.callback_query(F.data.regexp(USER_SETTINGS_COMPILE))
@inject
async def callback_user_settings(
    callback: CallbackQuery,
    user: "User",
    message_templater: FromDishka["TemplateMessageRenderer"],
    keyboard_templater: FromDishka["TemplateKeyboardRenderer"],
):
    """Callback обработчик взаимодействия с настройками"""
    button = USER_SETTINGS_COMPILE.match(callback.data).group(1)

    if button == "notifications":
        user.notifications_enabled = not user.notifications_enabled
    elif button == "profile_type":
        user.user_type = "teacher" if user.user_type == "student" else "student"
    elif button == "grouping_lessons":
        user.grouping_lessons = not user.grouping_lessons

    rendered_text = message_templater.render("user_settings", user=user)
    rendered_keyboard = keyboard_templater.user_settings(user)

    logger.info("Updating the message with the settings page")
    await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)
    logger.info("The message with the settings page has been updated")


@router.callback_query(F.data.regexp(OPEN_DAY_SCHEDULE_COMPILE))
@inject
async def callback_open_schedule(
    callback: CallbackQuery,
    user: "User",
    message_templater: FromDishka["TemplateMessageRenderer"],
    keyboard_templater: FromDishka["TemplateKeyboardRenderer"],
    use_case: FromDishka["GetDayScheduleUseCase"],
):
    """Callback обработчик открытия расписания"""
    schedule_for, schedule_item = OPEN_DAY_SCHEDULE_COMPILE.match(
        callback.data,
    ).groups()

    schedule_to: Literal["today", "tomorrow"] | None = None
    error = None

    for s_to in ("tomorrow", "today"):
        try:
            schedule_to: Literal["today", "tomorrow"] = s_to
            day_schedule = await use_case.execute(
                schedule_item, schedule_to, schedule_for, user.grouping_lessons
            )
            break
        except ScheduleDateNotFoundError as e:
            logger.warning("The schedule for %s has not been published", schedule_to)
            error = e
        except (ScheduleForGroupNotFoundError, ScheduleForCabinetNotFoundError) as e:
            logger.warning(
                "The schedule for %s %s for %s is unavailable",
                schedule_for,
                schedule_item,
                schedule_to,
            )
            error = e
    else:
        logger.warning(
            "The schedule for %s %s has not been found",
            schedule_for,
            schedule_item,
        )
        return await callback.answer(f"⚠ {error!s}")

    rendered_text = message_templater.render(
        "day_schedule",
        schedule_to=schedule_for,
        day_schedule=day_schedule,
    )
    rendered_keyboard = keyboard_templater.day_schedule(
        schedule_item,
        schedule_for,
        schedule_to,
    )

    logger.info("Changing the message to the schedule for %s", schedule_to)
    await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)
    logger.info("The message has been changed to the schedule for %s", schedule_to)

    return None


@router.callback_query(F.data.regexp(DAY_SCHEDULE_PANEL_COMPILE))
@inject
async def callback_day_schedule(
    callback: CallbackQuery,
    state: FSMContext,
    user: "User",
    time_zone: FromDishka[ZoneInfo],
    message_templater: FromDishka["TemplateMessageRenderer"],
    keyboard_templater: FromDishka["TemplateKeyboardRenderer"],
    day_schedule_use_case: FromDishka["GetDayScheduleUseCase"],
    unsubscribe_group_use_case: FromDishka["UnsubscribeGroupUseCase"],
    unsubscribe_cabinet_use_case: FromDishka["UnsubscribeCabinetUseCase"],
    all_groups_use_case: FromDishka["GetAllGroupsUseCase"],
    all_cabinets_use_case: FromDishka["GetAllCabinetsUseCase"],
):
    """Callback обработчик взаимодействия с кнопками расписания"""
    schedule_for, schedule_item, schedule_action, update = (
        DAY_SCHEDULE_PANEL_COMPILE.match(callback.data).groups()
    )

    if schedule_action in ["today", "tomorrow"]:
        updated_time = None

        if update:
            updated_time = datetime.datetime.now(time_zone)

        day_schedule = await day_schedule_use_case.execute(
            schedule_item,
            schedule_action,
            schedule_for,
        )

        rendered_text = message_templater.render(
            "day_schedule",
            schedule_to=schedule_for,
            day_schedule=day_schedule,
            updated_time=updated_time,
        )
        rendered_keyboard = keyboard_templater.day_schedule(
            schedule_item,
            schedule_for,
            schedule_action,
        )

        logger.info("Updating the message with the schedule page")
        await callback.message.edit_text(
            text=rendered_text,
            reply_markup=rendered_keyboard,
        )
        logger.info("The message with the schedule page has been updated")

        return None
    if schedule_action == "delete":
        try:
            if schedule_for == "group":
                await unsubscribe_group_use_case.execute(user, schedule_item)
                await callback.answer("✔ Вы перестали отслеживать группу")
            elif schedule_for == "cabinet":
                await unsubscribe_cabinet_use_case.execute(user, schedule_item)
                await callback.answer("✔ Вы перестали отслеживать кабинет")
        except (GroupUnsubscribeNotFoundError, CabinetUnsubscribeNotFoundError) as e:
            await callback.answer(f"⚠ {e!s}")

        is_student = user.user_type == "student"

        schedule_items = (
            await all_groups_use_case.execute()
            if is_student and user.group_subscribes
            else await all_cabinets_use_case.execute()
            if not is_student and user.cabinet_subscribes
            else []
        )

        user_state = UserStates.main_menu

        logger.info("Changing the user status to %s", user_state.state)
        await state.set_state(user_state)
        logger.info("The user status has been changed to %s", user_state.state)

        rendered_text = message_templater.render(
            "main_menu",
            user_tg=callback.from_user,
        )
        rendered_keyboard = keyboard_templater.main_menu(user, schedule_items)

        logger.info("Changing the message to the main menu")
        await callback.message.edit_text(
            text=rendered_text,
            reply_markup=rendered_keyboard,
        )
        logger.info("The message has been changed to the main menu")

        return None

    return None


@router.callback_query(F.data == "delete_message")
@inject
async def delete_message_callback(callback: CallbackQuery):
    """Callback обработчик удаления сообщения"""
    logger.info("Deleting a message")
    try:
        await callback.message.delete()
    except AiogramError as e:
        logger.warning("Error when deleting a message: %s", str(e))
        await callback.answer("⚠ Произошла техническая ошибка")
        logger.info("Clearing the reply_markup message")
        await callback.message.edit_reply_markup(reply_markup=None)
        logger.info("reply_markup messages successfully cleared")


@router.callback_query()
@inject
async def invalid_callback(callback: CallbackQuery):
    """Callback обработчик нереализованных кнопок"""
    logger.warning("The button has no useful functionality")
    return await callback.answer(
        "⚠ На данный момент данная кнопка не выполняет обработку",
    )
