import datetime
from typing import Literal

from .base_exceptions import DataRequestError


class UserNotFoundError(DataRequestError):
    """Ошибка отсутствия пользователя"""


class GroupNotFoundError(DataRequestError):
    """Ошибка отсутствия группы"""

    def __init__(self, group_number: str):
        super().__init__(f"Группа {group_number} не найдена")


class CabinetNotFoundError(DataRequestError):
    """Ошибка отсутствия кабинета"""

    def __init__(self, cabinet_number: str):
        self.cabinet_number = cabinet_number
        super().__init__(f"Кабинет {cabinet_number} не найден")


class GroupUnsubscribeNotFoundError(DataRequestError):
    """Ошибка отсутствия группы при отписке"""

    def __init__(self):
        super().__init__("Вы не отслеживаете расписание для данной группы")


class CabinetUnsubscribeNotFoundError(DataRequestError):
    """Ошибка отсутствия кабинета при отписке"""

    def __init__(self):
        super().__init__("Вы не отслеживаете расписание для данного кабинета")


class ScheduleDateNotFoundError(DataRequestError):
    """Ошибка получения даты расписания"""

    def __init__(self, schedule_to: Literal["today", "tomorrow"]):
        self.schedule_to = schedule_to
        super().__init__(
            f"Расписание на {'сегодня' if schedule_to == 'today' else 'завтра'} "
            f"еще не было опубликовано",
        )


class ScheduleForGroupNotFoundError(DataRequestError):
    """Ошибка получения расписания для группы"""

    def __init__(
        self,
        group,
        schedule_to: Literal["today", "tomorrow"],
        schedule_date: datetime.date,
    ):
        self.group = group
        self.schedule_to = schedule_to
        self.schedule_date = schedule_date
        super().__init__(
            f"Для кабинета {group!s} отсутствуют пары на "
            f"{'сегодня' if schedule_to == 'today' else 'завтра'} "
            f"({schedule_date.strftime('%d.%m.%Y г.')})",
        )


class ScheduleForCabinetNotFoundError(DataRequestError):
    """Ошибка получения расписания для кабинета"""

    def __init__(
        self,
        cabinet,
        schedule_to: Literal["today", "tomorrow"],
        schedule_date: datetime.date,
    ):
        self.cabinet = cabinet
        self.schedule_to = schedule_to
        self.schedule_date = schedule_date
        super().__init__(
            f"Для кабинета {cabinet!s} отсутствуют пары на "
            f"{'сегодня' if schedule_to == 'today' else 'завтра'} "
            f"({schedule_date.strftime('%d.%m.%Y г.')})",
        )
