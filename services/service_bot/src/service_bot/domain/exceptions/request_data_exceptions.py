from typing import Literal

from .base_exceptions import DataRequestError


class UserNotFound(DataRequestError):
    """Ошибка отсутствия пользователя"""


class GroupNotFound(DataRequestError):
    """Ошибка отсутствия группы"""

    def __init__(self, group_number: str):
        super().__init__(f"Группа {group_number} не найдена")


class CabinetNotFound(DataRequestError):
    """Ошибка отсутствия кабинета"""

    def __init__(self, cabinet_number: str):
        self.cabinet_number = cabinet_number
        super().__init__(f"Кабинет {cabinet_number} не найден")


class GroupUnsubscribeNotFound(DataRequestError):
    """Ошибка отсутствия группы при отписке"""

    def __init__(self):
        super().__init__('Вы не отслеживаете расписание для данной группы')


class CabinetUnsubscribeNotFound(DataRequestError):
    """Ошибка отсутствия кабинета при отписке"""

    def __init__(self):
        super().__init__('Вы не отслеживаете расписание для данного кабинета')


class ScheduleDateNotFound(DataRequestError):
    """Ошибка получения даты расписания"""

    def __init__(self, schedule_number: str, schedule_to: Literal['today', 'tomorrow']):
        self.schedule_number = schedule_number
        self.schedule_to = schedule_to
        super().__init__(f'Расписание на {'сегодня' if schedule_to == 'today' else 'завтра'} еще не было опубликовано')


class ScheduleForGroupNotFound(DataRequestError):
    """Ошибка получения расписания для группы"""

    def __init__(self, schedule_to: Literal['today', 'tomorrow']):
        self.schedule_to = schedule_to
        super().__init__(f'У группы нет пар на {'сегодня' if schedule_to == 'today' else 'завтра'}')


class ScheduleForCabinetNotFound(DataRequestError):
    """Ошибка получения расписания для кабинета"""

    def __init__(self, schedule_to: Literal['today', 'tomorrow']):
        self.schedule_to = schedule_to
        super().__init__(f'В кабинете отсутствуют пары на {'сегодня' if schedule_to == 'today' else 'завтра'}')
