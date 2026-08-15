# ====================== [БАЗОВЫЕ ИСКЛЮЧЕНИЯ] ======================
class ParserServiceError(BaseException):
    """Базовое исключение Parser Service"""


# ====================== [ОШИБКИ ВАЛИДАЦИИ] ======================
class ValidationError(ParserServiceError):
    """Ошибка валидации"""


class GroupNumberFormatError(ValidationError):
    """Ошибка формата номера группы"""


class GroupParserPositionError(ValidationError):
    """Ошибка координат GroupParser"""


class LessonEndTimeError(ValidationError):
    """Ошибка времени окончания пары"""


class LessonEmptyNameError(ValidationError):
    """Ошибка пустого названия пары"""


class LessonOverlapError(ParserServiceError):
    """Ошибка пересечения пары"""


class ScheduleForSomeGroupsError(ParserServiceError):
    """Ошибка передачи списка пар для нескольких групп"""


class ScheduleForSomeDatesError(ParserServiceError):
    """Ошибка передачи списка пар для нескольких дат"""


# ====================== [ОШИБКИ ОТСУТСТВИЯ ДАННЫХ] ======================
class NotFoundError(ParserServiceError):
    """Ошибка отсутствия данных"""


class GroupNotFoundError(NotFoundError):
    """Ошибка отсутствия группы"""


class CabinetNotFoundError(NotFoundError):
    """Ошибка отсутствия кабинета"""


class LessonNotFoundError(NotFoundError):
    """Ошибка отсутствия пары"""


class DayScheduleNotFoundError(NotFoundError):
    """Ошибка отсутствия пар на указанную дату"""


class SavingDayScheduleGroupNotFoundError(NotFoundError):
    """Ошибка отсутствия группы в списке пар"""


class SavingDayScheduleDateNotFoundError(NotFoundError):
    """Ошибка отсутствия даты в списке пар"""


# ====================== [ОШИБКИ ПАРСИНГА] ======================
class ParsingError(ParserServiceError):
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
