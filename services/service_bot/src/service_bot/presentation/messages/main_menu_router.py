import asyncio

from aiogram import Router
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
from service_bot.domain.entities import User
from service_bot.domain.exceptions import (
    CabinetAlreadyInsertedError,
    CabinetNotFound,
    GroupAlreadyInsertedError,
    GroupNotFound,
)
from service_bot.infrastructure.states import BotStates
from service_bot.infrastructure.template_system import (
    TemplateKeyboardRenderer,
    TemplateMessageRenderer,
)

router = Router()


async def delete_message_with_delay(message: Message, delay: float = 7.5):
    """Удаление сообщения спустя КД"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass


@router.message(or_f(Command('start'), StateFilter(None)))
@inject
async def message_open_main_menu(message: Message, state: FSMContext, user: 'User',
                                 message_templater: FromDishka['TemplateMessageRenderer'],
                                 keyboard_templater: FromDishka['TemplateKeyboardRenderer'],
                                 all_groups_use_case: FromDishka['GetAllGroupsUseCase'],
                                 all_cabinets_use_case: FromDishka['GetAllCabinetsUseCase']):
    """Обработчик команды /start и при State = None"""
    schedule_items = (
        await all_groups_use_case.execute()
        if user.user_type == 'student' and user.group_subscribes
        else await all_cabinets_use_case.execute()
        if user.user_type == 'teacher' and user.cabinet_subscribes
        else []
    )

    rendered_text = message_templater.render('main_menu', user_tg=message.from_user)
    rendered_keyboard = keyboard_templater.main_menu(user, schedule_items)

    panel = await message.answer(text=rendered_text, reply_markup=rendered_keyboard)

    user.message_panel_id = panel.message_id

    await state.set_state(BotStates.main_menu)


@router.message(StateFilter(BotStates.add_schedule_item))
@inject
async def message_add_schedule_item(message: Message, state: FSMContext, user: 'User',
                                    message_templater: FromDishka['TemplateMessageRenderer'],
                                    keyboard_templater: FromDishka['TemplateKeyboardRenderer'],
                                    get_group_use_case: FromDishka['GetGroupUseCase'],
                                    get_cabinet_use_case: FromDishka['GetCabinetUseCase'],
                                    subscribe_group_use_case: FromDishka['SubscribeGroupUseCase'],
                                    subscribe_cabinet_use_case: FromDishka['SubscribeCabinetUseCase'],
                                    all_groups_use_case: FromDishka['GetAllGroupsUseCase'],
                                    all_cabinets_use_case: FromDishka['GetAllCabinetsUseCase']):
    """Обработчик сообщения подписки на группу/кабинет"""
    is_student = user.user_type == 'student'

    try:
        if is_student:
            schedule_item = await get_group_use_case.execute(str(message.text))
            await subscribe_group_use_case.execute(user, schedule_item)
        else:
            schedule_item = await get_cabinet_use_case.execute(str(message.text))
            await subscribe_cabinet_use_case.execute(user, schedule_item)
    except (GroupNotFound, CabinetNotFound, GroupAlreadyInsertedError, CabinetAlreadyInsertedError) as e:
        error_message = await message.answer(text=f'⚠ {e!s}')
        asyncio.create_task(delete_message_with_delay(error_message))
        return

    success_rendered_message = message_templater.render('success_added_schedule_item', user=user,
                                                        schedule_item=schedule_item)
    success_message = await message.answer(text=success_rendered_message)
    asyncio.create_task(delete_message_with_delay(success_message))

    schedule_items = (
        await all_groups_use_case.execute()
        if is_student and user.group_subscribes
        else await all_cabinets_use_case.execute()
        if not is_student and user.cabinet_subscribes
        else []
    )

    rendered_text = message_templater.render('main_menu', user_tg=message.from_user)
    rendered_keyboard = keyboard_templater.main_menu(user, schedule_items)

    await message.bot.edit_message_text(chat_id=user.user_id, message_id=user.message_panel_id,
                                        text=rendered_text, reply_markup=rendered_keyboard)

    await state.set_state(BotStates.main_menu)
