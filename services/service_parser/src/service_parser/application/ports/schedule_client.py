from abc import ABC, abstractmethod
from typing import Literal, Any

from bs4 import BeautifulSoup
from numpy import ndarray, dtype


class ScheduleClient(ABC):
    @abstractmethod
    async def get_schedule_model(self, date_type: Literal['today', 'tomorrow']) -> BeautifulSoup:
        """Получение BeautifulSoup контента страницы"""
        raise NotImplementedError

    @abstractmethod
    def get_schedule_matrix(self, content: BeautifulSoup) -> ndarray[tuple[int, int], dtype[Any]]:
        """Получение матрицы страницы"""
        raise NotImplementedError
