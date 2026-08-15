# ====================== [БАЗОВЫЕ ИСКЛЮЧЕНИЯ] ======================
class APIServiceError(Exception):
    """Базовое исключение API Service"""

    code: str = "INTERNAL_ERROR"
    default_message: str = "An internal error occurred"
    status_code: int = 500

    def __init__(self, message: str | None = None, extra: dict | None = None):
        self.message = message or self.default_message
        self.extra = extra or {}
        super().__init__(self.message)

    def to_api_error(self) -> dict:
        return {"code": self.code, "detail": self.message, "extra": self.extra}


# ====================== [ИСКЛЮЧЕНИЯ-РОДИТЕЛИ] ======================
class ValidationError(APIServiceError):
    """Ошибка валидации"""

    status_code: int = 422


class NotFoundError(APIServiceError):
    """Ошибка отсутствия данных"""

    status_code: int = 404


class CacheError(APIServiceError):
    """Ошибка кэша"""
