from collections.abc import Iterable

from .base_exceptions import DataValidationError


class UserMetadataMissingError(DataValidationError):
    """Ошибка отсутствия метаданных"""

    def __init__(self, missing_keys: Iterable[str]):
        self.missing_keys = missing_keys
        super().__init__(
            f"The following keys are missing from the user metadata: "
            f"{', '.join(missing_keys)}",
        )


class NotPositiveIntegerValueError(DataValidationError):
    """Ошибка неположительного числа"""


class InvalidDayScheduleLessonTypeError(DataValidationError):
    """Ошибка типа пар в расписании"""


class InvalidUserMetadataTypeError(DataValidationError):
    """Ошибка типа метаданных пользователя"""

    def __init__(self, required_type: type, metadata_type: type):
        self.metadata_type = metadata_type
        self.required_type = required_type

        super().__init__(
            f"Invalid type of user metadata (metadata type - {self.metadata_type}, "
            f"value type - {self.required_type})",
        )


class InvalidUserMetadataKeyError(DataValidationError):
    """Ошибка типа метаданных пользователя"""

    def __init__(self, key: str):
        self.key = key

        super().__init__(f"Invalid key of user metadata - {self.key!r}")
