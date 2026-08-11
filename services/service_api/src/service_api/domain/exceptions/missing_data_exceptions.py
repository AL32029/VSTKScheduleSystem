import datetime
from dataclasses import asdict
from typing import Literal

from service_api.domain.entities import Cabinet, Group

from .base_exceptions import NotFoundError


class GroupNotFound(NotFoundError):
    """Ошибка отсутствия группы"""
    code: str = "GROUP_NOT_FOUND"

    def __init__(self, group_number: str):
        message = f'Group with number {group_number!r} not found'
        extra = {
            'input_number': group_number
        }
        super().__init__(message, extra)


class CabinetNotFound(NotFoundError):
    """Ошибка отсутствия кабинета"""
    code: str = "CABINET_NOT_FOUND"

    def __init__(self, cabinet_number: str):
        message = f'Cabinet with number {cabinet_number!r} not found'
        extra = {
            'input_number': cabinet_number
        }
        super().__init__(message, extra)


class ScheduleDateNotFound(NotFoundError):
    """Ошибка отсутствия даты расписания в базе данных"""
    code: str = "SCHEDULE_DATE_NOT_FOUND"

    def __init__(self, schedule_to: Literal['today', 'tomorrow']):
        message = f'The schedule for {schedule_to} has not been published'
        extra = {
            'schedule_to': schedule_to
        }
        super().__init__(message, extra)


class GroupDayScheduleNotFound(NotFoundError):
    """Ошибка отсутствия пар для группы на указанную дату"""
    code: str = "SCHEDULE_FOR_GROUP_NOT_FOUND"

    def __init__(self, group_item: 'Group', schedule_to: Literal['today', 'tomorrow'], schedule_date: datetime.date):
        message = f'For the {group_item!s} group, there are no lessons scheduled for {schedule_to} ({schedule_date!s})'
        extra = {
            'item': asdict(group_item),
            'schedule_to': schedule_to,
            'schedule_date': schedule_date
        }
        super().__init__(message, extra)


class CabinetDayScheduleNotFound(NotFoundError):
    """Ошибка отсутствия пар для кабинета на указанную дату"""
    code: str = "SCHEDULE_FOR_CABINET_NOT_FOUND"

    def __init__(self, cabinet_item: 'Cabinet', schedule_to: Literal['today', 'tomorrow'],
                 schedule_date: datetime.date):
        message = (f'For the {cabinet_item!s} cabinet, there are no lessons scheduled for {schedule_to} '
                   f'({schedule_date!s})')
        extra = {
            'item': asdict(cabinet_item),
            'schedule_to': schedule_to,
            'schedule_date': schedule_date
        }
        super().__init__(message, extra)
