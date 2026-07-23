from typing import Any

import pytest
from bs4 import BeautifulSoup
from numpy import ndarray, dtype

from service_parser.domain.entities import Group, DaySchedule


@pytest.fixture
async def html_content(schedule_provider, httpx_mock) -> str:
    with open('./tests/fixtures/schedule.html', 'rb') as f:
        httpx_mock.add_response(
            method='GET',
            url='https://vgtk.by/schedule/lessons/day-tomorrow.php',
            content=f.read()
        )

    return await schedule_provider._fetch_html('https://vgtk.by/schedule/lessons/day-tomorrow.php')


@pytest.fixture
def html_table(schedule_provider, html_content) -> BeautifulSoup:
    return schedule_provider._fetch_table(html_content)


@pytest.fixture
def html_matrix(schedule_provider, html_table) -> ndarray[tuple[int, int], dtype[Any]]:
    return schedule_provider._parse_table_to_matrix(html_table)


@pytest.fixture
def lessons_extract(schedule_provider, html_matrix) -> dict[Group, tuple[DaySchedule, ...]]:
    date_list = schedule_provider._extract_dates(html_matrix)
    lessons_time = schedule_provider._extract_times(html_matrix)
    groups = schedule_provider._extract_groups(html_matrix)

    lessons_extract = schedule_provider._extract_lessons(html_matrix, date_list, lessons_time, groups)

    return lessons_extract
