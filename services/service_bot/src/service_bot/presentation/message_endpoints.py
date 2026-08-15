import asyncio
import logging

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from service_bot.application.services import (
    GetAllCabinetsUseCase,
    GetAllGroupsUseCase,
    GetCabinetUseCase,
    GetGroupUseCase,
    SubscribeCabinetUseCase,
    SubscribeGroupUseCase,
)
from service_bot.domain.context_vars import (
    message_id_var,
    request_id_var,
    update_id_var,
    user_id_var,
)
from service_bot.domain.entities import User
from service_bot.domain.exceptions import (
    CabinetAlreadyInsertedError,
    CabinetNotFoundError,
    GroupAlreadyInsertedError,
    GroupNotFoundError,
)
from service_bot.infrastructure.template_engine_items import (
    TemplateKeyboardRenderer,
    TemplateMessageRenderer,
)

from .user_states import UserStates

logger = logging.getLogger(__name__)

router = Router()


async def delete_message_with_delay(
    message: Message, request_id, update_id, user_id, message_id, delay: float = 7.5,
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


@router.message(or_f(Command("start"), StateFilter(None)))
@inject
async def message_open_main_menu(
    message: Message,
    state: FSMContext,
    user: "User",
    message_templater: FromDishka["TemplateMessageRenderer"],
    keyboard_templater: FromDishka["TemplateKeyboardRenderer"],
    all_groups_use_case: FromDishka["GetAllGroupsUseCase"],
    all_cabinets_use_case: FromDishka["GetAllCabinetsUseCase"],
):
    """Обработчик команды /start и при State = None"""
    schedule_items = (
        await all_groups_use_case.execute()
        if user.user_type == "student" and user.group_subscribes
        else await all_cabinets_use_case.execute()
        if user.user_type == "teacher" and user.cabinet_subscribes
        else []
    )

    rendered_text = message_templater.render("main_menu", user_tg=message.from_user)
    rendered_keyboard = keyboard_templater.main_menu(user, schedule_items)

    user_state = UserStates.main_menu

    logger.info("Changing the user status to %s", user_state.state)
    await state.set_state(user_state)
    logger.info("The user status has been changed to %s", user_state.state)

    logger.info("Sending a message with the main menu")
    panel = await message.answer(text=rendered_text, reply_markup=rendered_keyboard)
    logger.info("The message with the main menu has been sent")

    user.message_panel_id = panel.message_id


@router.message(StateFilter(UserStates.add_schedule_item))
@inject
async def message_add_schedule_item(
    message: Message,
    state: FSMContext,
    user: "User",
    message_templater: FromDishka["TemplateMessageRenderer"],
    keyboard_templater: FromDishka["TemplateKeyboardRenderer"],
    get_group_use_case: FromDishka["GetGroupUseCase"],
    get_cabinet_use_case: FromDishka["GetCabinetUseCase"],
    subscribe_group_use_case: FromDishka["SubscribeGroupUseCase"],
    subscribe_cabinet_use_case: FromDishka["SubscribeCabinetUseCase"],
    all_groups_use_case: FromDishka["GetAllGroupsUseCase"],
    all_cabinets_use_case: FromDishka["GetAllCabinetsUseCase"],
):
    """Обработчик сообщения подписки на группу/кабинет"""
    is_student = user.user_type == "student"

    try:
        if is_student:
            schedule_item = await get_group_use_case.execute(str(message.text))
            await subscribe_group_use_case.execute(user, schedule_item)
        else:
            schedule_item = await get_cabinet_use_case.execute(str(message.text))
            await subscribe_cabinet_use_case.execute(user, schedule_item)
    except (
            GroupNotFoundError,
            CabinetNotFoundError,
            GroupAlreadyInsertedError,
            CabinetAlreadyInsertedError,
    ) as e:
        error_message = await message.answer(text=f"⚠ {e!s}")
        asyncio.create_task(
            delete_message_with_delay(
                error_message,
                request_id_var.get(),
                update_id_var.get(),
                user_id_var.get(),
                message_id_var.get(),
            ),
        )
        return

    success_rendered_message = message_templater.render(
        "success_added_schedule_item", user=user, schedule_item=schedule_item,
    )
    success_message = await message.answer(text=success_rendered_message)
    asyncio.create_task(
        delete_message_with_delay(
            success_message,
            request_id_var.get(),
            update_id_var.get(),
            user_id_var.get(),
            message_id_var.get(),
        ),
    )

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

    rendered_text = message_templater.render("main_menu", user_tg=message.from_user)
    rendered_keyboard = keyboard_templater.main_menu(user, schedule_items)

    logger.info("Changing the message to the main menu")
    await message.bot.edit_message_text(
        chat_id=user.user_id,
        message_id=user.message_panel_id,
        text=rendered_text,
        reply_markup=rendered_keyboard,
    )
    logger.info("The message has been changed to the main menu")
    return
