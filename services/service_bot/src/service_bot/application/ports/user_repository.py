from abc import ABC, abstractmethod
from typing import Any

from service_bot.domain.entities import Cabinet, Group
from service_bot.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def save(self, user_id: int) -> 'User':
        """Регистрация пользователя в БД"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> 'User':
        """Получение пользователя по ID"""
        raise NotImplementedError

    @abstractmethod
    async def update_metadata(self, user: 'User', key: str, value: Any) -> None:
        """Изменение значения метаданных в БД"""
        raise NotImplementedError

    @abstractmethod
    async def subscribe_group(self, user: 'User', group: 'Group') -> None:
        """Подписка на группу"""
        raise NotImplementedError

    @abstractmethod
    async def subscribe_cabinet(self, user: 'User', cabinet: 'Cabinet') -> None:
        """Подписка на кабинет"""
        raise NotImplementedError

    @abstractmethod
    async def unsubscribe_group(self, user: 'User', group_index: str) -> None:
        """Отписка от группы"""
        raise NotImplementedError

    @abstractmethod
    async def unsubscribe_cabinet(self, user: 'User', cabinet_index: str) -> None:
        """Отписка от кабинета"""
        raise NotImplementedError
