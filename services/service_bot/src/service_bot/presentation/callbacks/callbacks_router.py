import datetime
from typing import Literal

from aiogram import F, Router
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
from service_bot.domain.entities import DaySchedule, User
from service_bot.domain.exceptions import (
    CabinetNotFound,
    CabinetUnsubscribeNotFound,
    GroupNotFound,
    GroupUnsubscribeNotFound,
    ScheduleForCabinetNotFound,
    ScheduleForGroupNotFound,
)
from service_bot.infrastructure.states import BotStates
from service_bot.infrastructure.template_system import (
    TemplateKeyboardRenderer,
    TemplateMessageRenderer,
)
from service_bot.presentation.schemas import (
    DAY_SCHEDULE_PANEL_COMPILE,
    OPEN_DAY_SCHEDULE_COMPILE,
    USER_SETTINGS_COMPILE,
)

router = Router()


@router.callback_query(F.data == 'open_main_menu')
@inject
async def callback_open_main_menu(callback: CallbackQuery, state: FSMContext, user: 'User',
                                  message_templater: FromDishka['TemplateMessageRenderer'],
                                  keyboard_templater: FromDishka['TemplateKeyboardRenderer'],
                                  all_groups_use_case: FromDishka['GetAllGroupsUseCase'],
                                  all_cabinets_use_case: FromDishka['GetAllCabinetsUseCase']):
    """Callback обработчик открытия главного меню"""
    schedule_items = (
        await all_groups_use_case.execute()
        if user.user_type == 'student' and user.group_subscribes
        else await all_cabinets_use_case.execute()
        if user.user_type == 'teacher' and user.cabinet_subscribes
        else []
    )

    rendered_text = message_templater.render('main_menu', user_tg=callback.from_user)
    rendered_keyboard = keyboard_templater.main_menu(user, schedule_items)

    await state.set_state(BotStates.main_menu)

    return await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)


@router.callback_query(F.data == 'add_schedule_item')
@inject
async def callback_add_schedule_item(callback: CallbackQuery, state: FSMContext, user: 'User',
                                     message_templater: FromDishka['TemplateMessageRenderer'],
                                     keyboard_templater: FromDishka['TemplateKeyboardRenderer']):
    """Callback обработчик открытия диалога добавления группы/кабинета"""
    rendered_text = message_templater.render('add_schedule_item', user=user)
    rendered_keyboard = keyboard_templater.to_main_menu()

    await state.set_state(BotStates.add_schedule_item)

    return await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)


@router.callback_query(F.data == 'open_settings')
@inject
async def callback_open_settings(callback: CallbackQuery, user: 'User',
                                 message_templater: FromDishka['TemplateMessageRenderer'],
                                 keyboard_templater: FromDishka['TemplateKeyboardRenderer']):
    """Callback обработчик открытия панели настроек"""
    rendered_text = message_templater.render('user_settings', user=user)
    rendered_keyboard = keyboard_templater.user_settings(user)

    return await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)


@router.callback_query(F.data.regexp(USER_SETTINGS_COMPILE))
@inject
async def callback_user_settings(callback: CallbackQuery, user: 'User',
                                 message_templater: FromDishka['TemplateMessageRenderer'],
                                 keyboard_templater: FromDishka['TemplateKeyboardRenderer']):
    """Callback обработчик взаимодействия с настройками"""
    button = USER_SETTINGS_COMPILE.match(callback.data).group(1)

    if button == 'notifications':
        user.notifications_enabled = not user.notifications_enabled
    elif button == 'profile_type':
        user.user_type = 'teacher' if user.user_type == 'student' else 'student'

    rendered_text = message_templater.render('user_settings', user=user)
    rendered_keyboard = keyboard_templater.user_settings(user)

    return await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)


@router.callback_query(F.data.regexp(OPEN_DAY_SCHEDULE_COMPILE))
@inject
async def callback_open_schedule(callback: CallbackQuery, message_templater: FromDishka['TemplateMessageRenderer'],
                                 keyboard_templater: FromDishka['TemplateKeyboardRenderer'],
                                 use_case: FromDishka['GetDayScheduleUseCase']):
    """Callback обработчик открытия расписания"""
    schedule_for, schedule_item = OPEN_DAY_SCHEDULE_COMPILE.match(callback.data).groups()

    try:
        schedule_to: Literal['today', 'tomorrow'] = 'tomorrow'
        day_schedule = await use_case.execute(schedule_item, schedule_to, schedule_for)
    except (GroupNotFound, CabinetNotFound) as e:
        return await callback.answer(f'⚠ {e!s}')
    except (ScheduleForGroupNotFound, ScheduleForCabinetNotFound):
        schedule_to: Literal['today', 'tomorrow'] = 'today'
        try:
            day_schedule = await use_case.execute(schedule_item, schedule_to, schedule_for)
        except (ScheduleForGroupNotFound, ScheduleForCabinetNotFound) as e:
            return await callback.answer(f'⚠ {e!s}')

    rendered_text = message_templater.render('day_schedule', schedule_to=schedule_for, day_schedule=day_schedule)
    rendered_keyboard = keyboard_templater.day_schedule(schedule_item, schedule_for, schedule_to)

    return await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)


@router.callback_query(F.data.regexp(DAY_SCHEDULE_PANEL_COMPILE))
@inject
async def callback_day_schedule(callback: CallbackQuery, user: 'User',
                                message_templater: FromDishka['TemplateMessageRenderer'],
                                keyboard_templater: FromDishka['TemplateKeyboardRenderer'],
                                day_schedule_use_case: FromDishka['GetDayScheduleUseCase'],
                                unsubscribe_group_use_case: FromDishka['UnsubscribeGroupUseCase'],
                                unsubscribe_cabinet_use_case: FromDishka['UnsubscribeCabinetUseCase'],
                                all_groups_use_case: FromDishka['GetAllGroupsUseCase'],
                                all_cabinets_use_case: FromDishka['GetAllCabinetsUseCase']):
    """Callback обработчик взаимодействия с кнопками расписания"""
    schedule_for, schedule_item, schedule_action, update = DAY_SCHEDULE_PANEL_COMPILE.match(callback.data).groups()

    if schedule_action in ['today', 'tomorrow']:
        updated_time = None

        if update:
            updated_time = datetime.datetime.now()

        day_schedule: DaySchedule | None = None

        try:
            day_schedule = await day_schedule_use_case.execute(schedule_item, schedule_action, schedule_for)
        except (GroupNotFound, CabinetNotFound) as e:
            return await callback.answer(f'⚠ {e!s}')
        except (ScheduleForGroupNotFound, ScheduleForCabinetNotFound) as e:
            await callback.answer(f'⚠ {e!s}')

        rendered_text = message_templater.render('day_schedule', schedule_to=schedule_for,
                                                 day_schedule=day_schedule, updated_time=updated_time)
        rendered_keyboard = keyboard_templater.day_schedule(schedule_item, schedule_for, schedule_action)

        return await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)
    elif schedule_action == 'delete':
        try:
            if schedule_for == 'group':
                await unsubscribe_group_use_case.execute(user, schedule_item)
                await callback.answer('✔ Вы успешно отписались от группы')
            elif schedule_for == 'cabinet':
                await unsubscribe_cabinet_use_case.execute(user, schedule_item)
                await callback.answer('✔ Вы успешно отписались от кабинета')
        except (GroupUnsubscribeNotFound, CabinetUnsubscribeNotFound) as e:
            await callback.answer(f'⚠ {e!s}')

        schedule_items = (
            await all_groups_use_case.execute()
            if user.user_type == 'student' and user.group_subscribes
            else await all_cabinets_use_case.execute()
            if user.user_type == 'teacher' and user.cabinet_subscribes
            else []
        )

        rendered_text = message_templater.render('main_menu', user_tg=callback.from_user)
        rendered_keyboard = keyboard_templater.main_menu(user, schedule_items)

        return await callback.message.edit_text(text=rendered_text, reply_markup=rendered_keyboard)

    return None


@router.callback_query()
@inject
async def invalid_callback(callback: CallbackQuery):
    """Callback обработчик нереализованных кнопок"""
    return await callback.answer('⚠ На данный момент данная кнопка не выполняет обработку')
