from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date
from typing import Literal

from service_parser.domain.entities import Cabinet, Group


class TasksRepository(ABC):
    @abstractmethod
    async def send_clear_cache_task(
        self,
        groups: Iterable[str],
        cabinets: Iterable[str],
        schedule_to: Literal["today", "tomorrow"],
    ):
        """Отправка задачи на очистку кэша в API"""
        raise NotImplementedError

    @abstractmethod
    async def send_notify_task(
        self,
        changes: dict[
            date,
            dict[
                Literal["group", "cabinet"],
                dict[Literal["new", "update", "remove"], set["Group | Cabinet"]],
            ],
        ],
    ):
        """Отправка задачи на уведомление пользователей в бота"""
        raise NotImplementedError
