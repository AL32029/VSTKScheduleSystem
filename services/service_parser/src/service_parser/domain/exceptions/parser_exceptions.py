# ====================== [БАЗОВЫЕ ИСКЛЮЧЕНИЯ] ======================
class ParserServiceException(BaseException):
    """Базовое исключение Parser Service"""
    pass


# ====================== [ОШИБКИ ВАЛИДАЦИИ] ======================
class ValidationError(ParserServiceException):
    """Ошибка валидации"""
    pass


class GroupNumberFormatError(ValidationError):
    """Ошибка формата номера группы"""
    pass


class GroupParserPositionError(ValidationError):
    """Ошибка координат GroupParser"""
    pass


class LessonEndTimeError(ValidationError):
    """Ошибка времени окончания пары"""
    pass


class LessonEmptyNameError(ValidationError):
    """Ошибка пустого названия пары"""
    pass


class LessonOverlapError(ParserServiceException):
    """Ошибка пересечения пары"""
    pass


class ScheduleForSomeGroupsError(ParserServiceException):
    """Ошибка передачи списка пар для нескольких групп"""
    pass


class ScheduleForSomeDatesError(ParserServiceException):
    """Ошибка передачи списка пар для нескольких дат"""
    pass


# ====================== [ОШИБКИ ОТСУТСТВИЯ ДАННЫХ] ======================
class NotFoundError(ParserServiceException):
    """Ошибка отсутствия данных"""
    pass


class GroupNotFound(NotFoundError):
    """Ошибка отсутствия группы"""
    pass


class CabinetNotFound(NotFoundError):
    """Ошибка отсутствия кабинета"""
    pass


class LessonNotFoundError(NotFoundError):
    """Ошибка отсутствия пары"""
    pass


class DayScheduleNotFound(NotFoundError):
    """Ошибка отсутствия пар на указанную дату"""
    pass


class SavingDayScheduleGroupNotFound(NotFoundError):
    """Ошибка отсутствия группы в списке пар"""
    pass


class SavingDayScheduleDateNotFound(NotFoundError):
    """Ошибка отсутствия даты в списке пар"""
    pass


# ====================== [ОШИБКИ ПАРСИНГА] ======================
class ParsingError(ParserServiceException):
    """Ошибка парсинга"""
    pass


class FetchingTableError(ParsingError):
    """Ошибка извлечения таблицы"""
    pass


class ScheduleUnchangedError(ParsingError):
    """Ошибка отсутствия изменений в расписании"""
    pass


class ParsingMatrixError(ParsingError):
    """Ошибка преобразования таблицы в матрицу"""
    pass


class ParsingDateError(ParsingError):
    """Ошибка парсинга даты расписания"""
    pass


class ParsingLessonTimesError(ParsingError):
    """Ошибка парсинга времени расписания"""
    pass


class ParsingGroupsError(ParsingError):
    """Ошибка парсинга групп"""
    pass


class ParsingDayScheduleError(ParsingError):
    """Ошибка парсинга расписания пар"""
    pass
