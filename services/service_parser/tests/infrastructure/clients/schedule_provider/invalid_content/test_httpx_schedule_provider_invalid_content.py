from bs4 import BeautifulSoup


def test_get_schedule_table_with_empty_content(schedule_provider):
    table = schedule_provider._fetch_table(' ')

    assert table is None


def test_get_schedule_matrix_with_empty_table(schedule_provider):
    table = BeautifulSoup('', 'lxml')
    matrix = schedule_provider._parse_table_to_matrix(table)

    assert matrix is None


def test_get_schedule_dates_with_invalid_dates(schedule_provider, html_matrix):
    dates = schedule_provider._extract_dates(html_matrix)

    assert dates is None
