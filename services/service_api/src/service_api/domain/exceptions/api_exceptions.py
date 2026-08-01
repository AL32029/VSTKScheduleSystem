# ====================== [БАЗОВЫЕ ИСКЛЮЧЕНИЯ] ======================
class APIServiceException(BaseException):
    """Базовое исключение API Service"""


# ====================== [ОШИБКИ ВАЛИДАЦИИ] ======================
class ValidationError(APIServiceException):
    """Ошибка валидации"""


class GroupNumberFormatError(ValidationError):
    """Ошибка формата номера группы"""


class LessonEndTimeError(ValidationError):
    """Ошибка времени окончания пары"""


class DayScheduleEmptyLessonsError(ValidationError):
    """Ошибка пустого расписания"""


# ====================== [ОШИБКИ ОТСУТСТВИЯ ДАННЫХ] ======================
class NotFoundError(APIServiceException):
    """Ошибка отсутствия данных"""


class GroupNotFound(NotFoundError):
    """Ошибка отсутствия группы"""


class CabinetNotFound(NotFoundError):
    """Ошибка отсутствия кабинета"""


class ScheduleDateNotFound(NotFoundError):
    """Ошибка отсутствия даты расписания в базе данных"""


class GroupDayScheduleNotFound(NotFoundError):
    """Ошибка отсутствия пар для группы на указанную дату"""


class CabinetDayScheduleNotFound(NotFoundError):
    """Ошибка отсутствия пар для кабинета на указанную дату"""
