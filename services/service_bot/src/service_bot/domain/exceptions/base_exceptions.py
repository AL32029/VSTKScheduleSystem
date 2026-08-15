class BotServiceException(Exception):
    """Базовое исключение Bot Service"""


class DataRequestError(BotServiceException):
    """Ошибка запроса данных"""


class DataSavingError(BotServiceException):
    """Ошибка сохранения данных"""


class DataValidationError(BotServiceException):
    """Ошибка валидации данных"""
