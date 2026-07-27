import pytest

from service_parser.domain.exceptions.parser_exceptions import FetchingTableError, ParsingMatrixError, ParsingDateError


# ===================== [ТЕСТЫ ОШИБКИ FetchingTableError] =====================
def test_fetch_schedule_table_error(schedule_provider, html_content_invalid_table_class):
    """Тест должен выдать ошибку FetchingTableError"""
    with pytest.raises(FetchingTableError) as exc_info:
        schedule_provider._fetch_table(html_content_invalid_table_class)

    assert exc_info.value.args[0] == f'The HTML content does not contain a <table> with the class {'excel'!r}'


# ===================== [ТЕСТЫ ОШИБКИ ParsingMatrixError] =====================
@pytest.mark.parametrize('html_fixture, expected_message', [
    ('html_content_without_rows', 'The schedule table does not contain any rows'),
    ('html_content_without_columns', 'The schedule table does not contain any columns'),
])
def test_parse_table_to_matrix_errors(schedule_provider, request, html_fixture, expected_message):
    """Тест должен выдать ошибку ParsingMatrixError при отсутствии строк или колонок"""
    table = schedule_provider._fetch_table(request.getfixturevalue(html_fixture))

    with pytest.raises(ParsingMatrixError) as exc_info:
        schedule_provider._parse_table_to_matrix(table)

    assert exc_info.value.args[0] == expected_message


# ===================== [ТЕСТЫ ОШИБКИ ParsingDateError] =====================
@pytest.mark.parametrize('html_fixture, expected_message', [
    ('html_content_with_invalid_date_format', 'The schedule table does not contain a schedule '
                                              'date with a predefined format'),
    ('html_content_with_older_date', 'The schedule table does not contain the schedule date after '
                                     'checking the items for date compliance'),
])
def test_extract_dates_errors(schedule_provider, request, html_fixture, expected_message):
    """Тест должен выдать ошибку ParsingDateError при некорректном формате даты либо устаревшем расписании"""
    table = schedule_provider._fetch_table(request.getfixturevalue(html_fixture))
    matrix = schedule_provider._parse_table_to_matrix(table)

    with pytest.raises(ParsingDateError) as exc_info:
        schedule_provider._extract_dates(matrix)

    assert exc_info.value.args[0] == expected_message

# ===================== [ТЕСТЫ ОШИБКИ ParsingLessonTimesError] =====================
# [MISC][TODO][HIGH] Реализовать тесты ошибки ParsingLessonTimesError

# ===================== [ТЕСТЫ ОШИБКИ ParsingGroupsError] =========
# [MISC][TODO][HIGH] Реализовать тесты ошибки ParsingGroupsErrorngGroupsError

# ===================== [ТЕСТЫ ОШИБКИ ParsingDayScheduleError] =========
# [MISC][TODO][HIGH] Реализовать тесты ошибки ParsingDayScheduleErrorScheduleError
