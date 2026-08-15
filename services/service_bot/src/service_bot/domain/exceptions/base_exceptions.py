class BotServiceError(Exception):
    """Базовое исключение Bot Service"""


class DataRequestError(BotServiceError):
    """Ошибка запроса данных"""


class DataSavingError(BotServiceError):
    """Ошибка сохранения данных"""


class DataValidationError(BotServiceError):
    """Ошибка валидации данных"""
