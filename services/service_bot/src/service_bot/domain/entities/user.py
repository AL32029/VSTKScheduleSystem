from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal, cast

from service_bot.domain.exceptions import (
    InvalidUserMetadataKey,
    InvalidUserMetadataType,
    NotPositiveIntegerValueError,
    UserMetadataMissingError,
)


@dataclass
class User:
    """Сущность пользователя бота"""
    _DEFAULT_METADATA: ClassVar[dict] = {
        'user_type': 'student',
        'notifications_enabled': True,
        'is_admin': False,
        'message_panel_id': None,
        'grouping_lessons': True
    }
    _REQUIRED_METADATA: ClassVar[frozenset] = frozenset(_DEFAULT_METADATA.keys())

    user_id: int

    metadata: dict[str, Any] = field(
        default_factory=lambda: User._DEFAULT_METADATA.copy()
    )

    group_subscribes: Iterable[str] = field(default_factory=list)
    cabinet_subscribes: Iterable[str] = field(default_factory=list)

    def __post_init__(self):
        if self.user_id < 1:
            raise NotPositiveIntegerValueError('The user ID must be a positive number')

        if missing := self._REQUIRED_METADATA - self.metadata.keys():
            raise UserMetadataMissingError(missing)

        if not isinstance(self.group_subscribes, list):
            self.group_subscribes = list(self.group_subscribes)

        if not isinstance(self.cabinet_subscribes, list):
            self.cabinet_subscribes = list(self.cabinet_subscribes)

    @property
    def user_type(self) -> Literal['student', 'teacher']:
        """Тип пользователя [student/teacher]"""
        return cast(Literal['student', 'teacher'], self.metadata.get('user_type'))

    @user_type.setter
    def user_type(self, new_value: Literal['student', 'teacher']) -> None:
        """Установка типа пользователя"""
        self.update_metadata('user_type', new_value)

    @property
    def notifications_enabled(self) -> bool:
        """Статус уведомлений об изменениях в расписании"""
        return cast(bool, self.metadata.get('notifications_enabled'))

    @notifications_enabled.setter
    def notifications_enabled(self, new_status: bool) -> None:
        """Изменение статуса уведомлений об изменениях в расписании"""
        self.update_metadata('notifications_enabled', new_status)

    @property
    def is_admin(self) -> bool:
        """Статус наличия админ-прав"""
        return cast(bool, self.metadata.get('is_admin'))

    @is_admin.setter
    def is_admin(self, new_status: bool) -> None:
        """Изменение статуса наличия админ-прав"""
        self.update_metadata('is_admin', new_status)

    @property
    def message_panel_id(self) -> int | None:
        """ID сообщения с панелью управления"""
        return self.metadata.get('message_panel_id')

    @message_panel_id.setter
    def message_panel_id(self, message_id: int) -> None:
        """Изменение ID сообщения с панелью управления"""
        self.update_metadata('message_panel_id', message_id)

    def update_metadata(self, key: str, value: Any) -> None:
        """Обновление метаданных по ключу"""
        if key not in self.metadata:
            raise InvalidUserMetadataKey(key)

        if self.metadata[key] is not None and type(self.metadata[key]) != type(value):
            raise InvalidUserMetadataType(type(self.metadata[key]), type(value))

        self.metadata[key] = value
