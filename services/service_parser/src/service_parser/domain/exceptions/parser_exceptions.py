# ====================== [БАЗОВЫЕ ИСКЛЮЧЕНИЯ] ======================
class ParserServiceException(BaseException):
    """Базовое исключение Parser Service"""


# ====================== [ОШИБКИ ВАЛИДАЦИИ] ======================
class ValidationError(ParserServiceException):
    """Ошибка валидации"""


class GroupNumberFormatError(ValidationError):
    """Ошибка формата номера группы"""


class GroupParserPositionError(ValidationError):
    """Ошибка координат GroupParser"""


class LessonEndTimeError(ValidationError):
    """Ошибка времени окончания пары"""


class LessonEmptyNameError(ValidationError):
    """Ошибка пустого названия пары"""


class LessonOverlapError(ParserServiceException):
    """Ошибка пересечения пары"""


class ScheduleForSomeGroupsError(ParserServiceException):
    """Ошибка передачи списка пар для нескольких групп"""


class ScheduleForSomeDatesError(ParserServiceException):
    """Ошибка передачи списка пар для нескольких дат"""


# ====================== [ОШИБКИ ОТСУТСТВИЯ ДАННЫХ] ======================
class NotFoundError(ParserServiceException):
    """Ошибка отсутствия данных"""


class GroupNotFound(NotFoundError):
    """Ошибка отсутствия группы"""


class CabinetNotFound(NotFoundError):
    """Ошибка отсутствия кабинета"""


class LessonNotFoundError(NotFoundError):
    """Ошибка отсутствия пары"""


class DayScheduleNotFound(NotFoundError):
    """Ошибка отсутствия пар на указанную дату"""


class SavingDayScheduleGroupNotFound(NotFoundError):
    """Ошибка отсутствия группы в списке пар"""


class SavingDayScheduleDateNotFound(NotFoundError):
    """Ошибка отсутствия даты в списке пар"""


# ====================== [ОШИБКИ ПАРСИНГА] ======================
class ParsingError(ParserServiceException):
    """Ошибка парсинга"""


class FetchingTableError(ParsingError):
    """Ошибка извлечения таблицы"""


class ScheduleUnchangedError(ParsingError):
    """Ошибка отсутствия изменений в расписании"""


class ParsingMatrixError(ParsingError):
    """Ошибка преобразования таблицы в матрицу"""


class ParsingDateError(ParsingError):
    """Ошибка парсинга даты расписания"""


class ParsingLessonTimesError(ParsingError):
    """Ошибка парсинга времени расписания"""


class ParsingGroupsError(ParsingError):
    """Ошибка парсинга групп"""


class ParsingDayScheduleError(ParsingError):
    """Ошибка парсинга расписания пар"""
