import asyncio
import logging

from aiogram import Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message

from service_bot.domain.context_vars import (
    message_id_var,
    request_id_var,
    update_id_var,
    user_id_var,
)
from service_bot.domain.exceptions import (
    APIRequestTimedOutError,
    CabinetAlreadyInsertedError,
    CabinetNotFoundError,
    GroupAlreadyInsertedError,
    GroupNotFoundError,
    ScheduleDateNotFoundError,
    ScheduleForCabinetNotFoundError,
    ScheduleForGroupNotFoundError,
)

from .actions import delete_message_with_delay

router = Router()

logger = logging.getLogger(__name__)


def _log_group_not_found(exc: GroupNotFoundError) -> str:
    return f"The group {exc.group_number} was not found"


def _log_cabinet_not_found(exc: CabinetNotFoundError) -> str:
    return f"The cabinet {exc.cabinet_number} was not found"


def _log_timeout(exc: APIRequestTimedOutError) -> str:
    return f"It was not possible to retrieve info from {exc.endpoint} — timeout"


def _log_schedule_date_not_found(exc: ScheduleDateNotFoundError) -> str:
    return f"The schedule for {exc.schedule_to} has not been published"


def _log_schedule_for_group_not_found(exc: ScheduleForGroupNotFoundError) -> str:
    return f"The schedule for group {exc.group} for {exc.schedule_to} is unavailable"


def _log_schedule_for_cabinet_not_found(exc: ScheduleForCabinetNotFoundError) -> str:
    return (
        f"The schedule for cabinet {exc.cabinet} for {exc.schedule_to} is unavailable"
    )


def _log_duplicate_insert(
    exc: GroupAlreadyInsertedError | CabinetAlreadyInsertedError,
) -> str:
    if isinstance(exc, GroupAlreadyInsertedError):
        return f"Group {exc.group_number} already inserted"
    else:
        return f"Cabinet {exc.cabinet_number} already inserted"


LOG_MAP = {
    GroupNotFoundError: _log_group_not_found,
    CabinetNotFoundError: _log_cabinet_not_found,
    APIRequestTimedOutError: _log_timeout,
    ScheduleDateNotFoundError: _log_schedule_date_not_found,
    ScheduleForGroupNotFoundError: _log_schedule_for_group_not_found,
    ScheduleForCabinetNotFoundError: _log_schedule_for_cabinet_not_found,
    GroupAlreadyInsertedError: _log_duplicate_insert,
    CabinetAlreadyInsertedError: _log_duplicate_insert,
}


@router.error(
    ExceptionTypeFilter(
        GroupNotFoundError,
        CabinetNotFoundError,
        APIRequestTimedOutError,
        ScheduleDateNotFoundError,
        GroupAlreadyInsertedError,
        CabinetAlreadyInsertedError,
        ScheduleForGroupNotFoundError,
        ScheduleForCabinetNotFoundError,
    )
)
async def handle_known_errors(event: ErrorEvent):
    exception = event.exception
    instance = event.update.message or event.update.callback_query or None

    if instance is None:
        return None

    log_func = LOG_MAP.get(type(exception))
    if log_func:
        logger.warning(log_func(exception))

    error_message = await instance.answer(f"⚠ {exception!s}")

    if isinstance(instance, Message):
        asyncio.create_task(
            delete_message_with_delay(
                error_message,
                request_id_var.get(),
                update_id_var.get(),
                user_id_var.get(),
                message_id_var.get(),
            )
        )

    return None
