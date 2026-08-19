from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date
from typing import Literal


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
            Literal["group", "cabinet"],
            dict[Literal["new", "update", "remove"], set[str]],
        ],
        schedule_to: Literal["today", "tomorrow"],
        dates: date | tuple[date, date],
    ):
        """Отправка задачи на уведомление пользователей в бота"""
        raise NotImplementedError
