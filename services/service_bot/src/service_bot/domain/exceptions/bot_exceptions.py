from collections.abc import Iterable
from typing import Literal


# ====================== [БАЗОВЫЕ ИСКЛЮЧЕНИЯ] ======================
class BotServiceException(Exception):
    """Базовое исключение Bot Service"""


# ====================== [ОШИБКА ЗАПРОСА ДАННЫХ] ======================
class DataRequestError(BotServiceException):
    """Ошибка запроса данных"""


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
        super().__init__('Вы не подписаны на данную группу')


class CabinetUnsubscribeNotFound(DataRequestError):
    """Ошибка отсутствия кабинета при отписке"""

    def __init__(self):
        super().__init__('Вы не подписаны на данный кабинет')


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


# ====================== [ОШИБКА СОХРАНЕНИЯ ДАННЫХ] ======================
class DataSavingError(BotServiceException):
    """Ошибка сохранения данных"""


class GroupAlreadyInsertedError(DataSavingError):
    """Ошибка сохранения уже добавленной группы"""

    def __init__(self, group_number: str):
        self.group_number = group_number
        super().__init__(f"У вас уже добавлена группа {group_number}")


class CabinetAlreadyInsertedError(DataSavingError):
    """Ошибка сохранения уже добавленного кабинета"""

    def __init__(self, cabinet_number: str):
        self.cabinet_number = cabinet_number
        super().__init__(f"У вас уже добавлен кабинет {cabinet_number}")


# ====================== [ОШИБКА ВАЛИДАЦИИ ДАННЫХ] ======================
class DataValidationError(BotServiceException):
    """Ошибка валидации данных"""


class UserMetadataMissingError(DataValidationError):
    """Ошибка отсутствия метаданных"""

    def __init__(self, missing_keys: Iterable[str]):
        self.missing_keys = missing_keys
        super().__init__(f"The following keys are missing from the user metadata: {', '.join(missing_keys)}")


class NotPositiveIntegerValueError(DataValidationError):
    """Ошибка неположительного числа"""


class InvalidDayScheduleLessonType(DataValidationError):
    """Ошибка типа пар в расписании"""


class InvalidUserMetadataType(DataValidationError):
    """Ошибка типа метаданных пользователя"""

    def __init__(self, required_type: type, metadata_type: type):
        self.metadata_type = metadata_type
        self.required_type = required_type

        super().__init__(f'Invalid type of user metadata (metadata type - {self.metadata_type}, '
                         f'value type - {self.required_type})')


class InvalidUserMetadataKey(DataValidationError):
    """Ошибка типа метаданных пользователя"""

    def __init__(self, key: str):
        self.key = key

        super().__init__(f'Invalid key of user metadata - {self.key!r}')
