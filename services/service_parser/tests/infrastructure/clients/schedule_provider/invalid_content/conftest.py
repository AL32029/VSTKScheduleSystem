from typing import Any

import pytest
from numpy import ndarray, dtype


@pytest.fixture
async def html_content(schedule_provider, httpx_mock) -> str:
    with open('./tests/fixtures/schedule_invalid_date_format.html', 'rb') as f:
        httpx_mock.add_response(
            method='GET',
            url='https://vgtk.by/schedule/lessons/day-tomorrow.php',
            content=f.read()
        )

    return await schedule_provider._fetch_html('https://vgtk.by/schedule/lessons/day-tomorrow.php')


@pytest.fixture
def html_matrix(schedule_provider, html_content) -> ndarray[tuple[
    int, int], dtype[Any]]:
    table = schedule_provider._fetch_table(html_content)

    return schedule_provider._parse_table_to_matrix(table)
