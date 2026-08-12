import datetime
from typing import Any

import aiofiles
import pytest
from bs4 import BeautifulSoup
from numpy import dtype, ndarray

from service_parser.domain.entities import GroupParser


@pytest.fixture
async def html_content(schedule_provider, httpx_mock) -> str:
    """Мок HTLM-контента страницы с расписанием"""
    async with aiofiles.open('./tests/fixtures/schedule.html', 'rb') as f:
        httpx_mock.add_response(
            method='GET',
            url='https://vgtk.by/schedule/lessons/day-tomorrow.php',
            content=await f.read()
        )

    return await schedule_provider._fetch_html('https://vgtk.by/schedule/lessons/day-tomorrow.php')


@pytest.fixture
def html_table(schedule_provider, html_content) -> BeautifulSoup:
    """BeautifulSoup модель таблицы расписания"""
    return schedule_provider._fetch_table(html_content)


@pytest.fixture
def html_matrix(schedule_provider, html_table) -> ndarray[tuple[int, int], dtype[Any]]:
    """NumPy матрица таблицы расписания"""
    return schedule_provider._parse_table_to_matrix(html_table)


@pytest.fixture
def schedule_dates(schedule_provider, html_matrix) -> tuple[datetime.date, ...]:
    """Дата расписания"""
    return schedule_provider._extract_dates(html_matrix)


@pytest.fixture
def schedule_times(schedule_provider, html_matrix) -> tuple[tuple[datetime.time, datetime.time], ...]:
    """Временные диапазоны расписания"""
    return schedule_provider._extract_times(html_matrix)


@pytest.fixture
def schedule_groups(schedule_provider, html_matrix) -> tuple[GroupParser, ...]:
    """Группы"""
    return schedule_provider._extract_groups(html_matrix)
