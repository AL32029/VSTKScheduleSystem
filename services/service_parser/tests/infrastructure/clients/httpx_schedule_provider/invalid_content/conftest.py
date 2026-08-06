import aiofiles
import pytest


# ===================== [ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ] =====================
async def _html_invalid_scenario(schedule_provider, httpx_mock, file_name) -> str:
    """Фикстура, возвращающая HTML для разных сценариев ошибок"""
    file_path = f'./tests/fixtures/invalid_schedules/{file_name}'
    async with aiofiles.open(file_path, 'rb') as f:
        httpx_mock.add_response(
            method='GET',
            url='https://vgtk.by/schedule/lessons/day-tomorrow.php',
            content=f.read()
        )
    return await schedule_provider._fetch_html('https://vgtk.by/schedule/lessons/day-tomorrow.php')


# ===================== [ОСНОВНЫЕ ФИКСТУРЫ] =====================
@pytest.fixture
async def html_content_invalid_table_class(schedule_provider, httpx_mock) -> str:
    """HTML страница с некоррктным названием класса"""
    return await _html_invalid_scenario(schedule_provider, httpx_mock, 'schedule_invalid_table_class.html')


# ===================== [ОТСУТСТВУЮЩИЕ СТРОКИ/СТОЛБЦЫ] =====================
@pytest.fixture
async def html_content_without_rows(schedule_provider, httpx_mock) -> str:
    """HTML страница без строк в расписании"""
    return await _html_invalid_scenario(schedule_provider, httpx_mock, 'schedule_without_rows.html')


@pytest.fixture
async def html_content_without_columns(schedule_provider, httpx_mock) -> str:
    """HTML страница без столбцов в расписании"""
    return await _html_invalid_scenario(schedule_provider, httpx_mock, 'schedule_without_columns.html')


# ===================== [НЕКОРРЕКТНЫЕ ДАТЫ] =====================
@pytest.fixture
async def html_content_with_invalid_date_format(schedule_provider, httpx_mock) -> str:
    """HTML страница с некорректным форматом дат"""
    return await _html_invalid_scenario(schedule_provider, httpx_mock, 'schedule_invalid_date_format.html')


@pytest.fixture
async def html_content_with_older_date(schedule_provider, httpx_mock) -> str:
    """HTML страница с устаревшим расписанием"""
    return await _html_invalid_scenario(schedule_provider, httpx_mock, 'schedule_with_older_date.html')


# ===================== [НЕКОРРЕКТНОЕ ВРЕМЯ ПАР] =====================
@pytest.fixture
async def html_content_with_invalid_time_format(schedule_provider, httpx_mock) -> str:
    """HTML страница с некорректным форматом временных промежутков"""
    return await _html_invalid_scenario(schedule_provider, httpx_mock, 'schedule_invalid_time_format.html')


# ===================== [НЕКОРРЕКТНЫЙ НОМЕР ГРУППЫ] =====================
@pytest.fixture
async def html_content_with_invalid_group_format(schedule_provider, httpx_mock) -> str:
    """HTML страница с некорректным форматом номера группы"""
    return await _html_invalid_scenario(schedule_provider, httpx_mock, 'schedule_invalid_group_format.html')

# ===================== [ПУСТОЕ РАСПИСАНИЕ] =====================
@pytest.fixture
async def html_content_without_lessons(schedule_provider, httpx_mock) -> str:
    """HTML страница с пустым расписанием"""
    return await _html_invalid_scenario(schedule_provider, httpx_mock, 'schedule_without_lessons.html')
