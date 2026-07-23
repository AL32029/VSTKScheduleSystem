class ParserServiceException(BaseException):
    """Базовое исключение Parser Service"""
    pass


class InvalidGroupNumberFormatError(ParserServiceException):
    """Ошибка формата номера группы"""
    pass


class NegativeGroupPositionError(ParserServiceException):
    """Ошибка отрицательной координаты GroupParser"""
    pass


class InvalidLessonEndTime(ParserServiceException):
    """Ошибка раннего времени окончания пары относительно времени начала пары"""
    pass


class MissingLessonNameError(ParserServiceException):
    """Ошибка пустого названия пары"""
    pass


class LessonNotFoundError(ParserServiceException):
    """Ошибка отсутствия пары"""
    pass


class LessonOverlapError(ParserServiceException):
    """Ошибка пересечения пары"""
    pass

class ScheduleGroupNotFound(ParserServiceException):
    """Ошибка отсутствия группы"""
    pass

class ScheduleCabinetNotFound(ParserServiceException):
    """Ошибка отсутствия кабинета"""
    pass

class DayScheduleNotFound(ParserServiceException):
    """Ошибка отсутствия пар на указанную дату"""
    pass

class SendingScheduleForSomeGroups(ParserServiceException):
    """Ошибка передачи списка пар для нескольких групп"""
    pass

class SendingScheduleForSomeDates(ParserServiceException):
    """Ошибка передачи списка пар для нескольких дат"""
    pass

class SendingScheduleGroupNotFound(ParserServiceException):
    """Ошибка отсутствия группы в списке пар"""
    pass

class SendingScheduleDateNotFound(ParserServiceException):
    """Ошибка отсутствия даты в списке пар"""
    pass