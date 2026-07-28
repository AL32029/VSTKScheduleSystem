import datetime

from service_parser.domain.entities import GroupParser, Group


def test_extract_schedule_dates(schedule_provider, html_matrix):
    """Тест должен извлечь из матрицы расписания 1 дату расписания - 31.12.2099"""
    schedule_dates = schedule_provider._extract_dates(html_matrix)

    assert schedule_dates
    assert len(schedule_dates) == 1

    schedule_date = schedule_dates[0]
    assert isinstance(schedule_date, datetime.date)
    assert schedule_date == datetime.date(2099, 12, 31)


def test_extract_schedule_times(schedule_provider, html_matrix):
    """Тест должен извлечь из матрицы 11 временных диапазонов пар"""
    schedule_times = schedule_provider._extract_times(html_matrix)

    assert schedule_times
    assert len(schedule_times) == 11
    assert len(set(schedule_times)) == 11
    assert schedule_times == tuple(sorted(schedule_times, key=lambda x: x[0]))
    assert all(isinstance(schedule_time, tuple)
               and len(schedule_time) == 2
               and isinstance(schedule_time[0], datetime.time)
               and isinstance(schedule_time[1], datetime.time)
               and schedule_time[0] < schedule_time[1]
               for schedule_time in schedule_times)


def test_extract_schedule_groups(schedule_provider, html_matrix):
    """Тест должен извлечь из матрицы 64 группы"""
    schedule_groups = schedule_provider._extract_groups(html_matrix)

    assert schedule_groups
    assert len(schedule_groups) == 64
    assert len(set(schedule_groups)) == 64
    assert schedule_groups == tuple(sorted(schedule_groups, key=lambda x: x.group.index))
    assert all(isinstance(schedule_group, GroupParser)
               for schedule_group in schedule_groups)


def test_extract_schedule_lessons(schedule_provider, html_matrix, schedule_dates, schedule_times, schedule_groups):
    """Тест должен извлечь расписание из матрицы"""
    schedule = schedule_provider._extract_lessons(html_matrix, schedule_dates, schedule_times, schedule_groups)

    assert schedule
    assert len(schedule.keys()) == 64
    assert len(set(schedule.keys())) == 64
    assert all(isinstance(group, Group)
               for group in schedule.keys())
    assert all(len(day_schedules) == 1 for day_schedules in schedule.values())
    assert all(day_schedule.lessons == tuple(sorted(day_schedule.lessons, key=lambda x: x.start))
               for day_schedules in schedule.values() if day_schedules
               for day_schedule in day_schedules if day_schedule.lessons)


async def test_get_schedule_for_groups(schedule_provider, httpx_mock):
    """Тест должен провести полный цикл парсинга расписания"""
    with open('./tests/fixtures/schedule.html', 'rb') as f:
        httpx_mock.add_response(
            method='GET',
            url='https://vgtk.by/schedule/lessons/day-tomorrow.php',
            content=f.read()
        )

    schedule = await schedule_provider.get_schedule_for_groups()

    assert schedule
    assert len(schedule.keys()) == 64
    assert len(set(schedule.keys())) == 64
    assert all(isinstance(group, Group)
               for group in schedule.keys())
    assert all(len(day_schedules) == 1 for day_schedules in schedule.values())
    assert all(day_schedule.lessons == tuple(sorted(day_schedule.lessons, key=lambda x: x.start))
               for day_schedules in schedule.values() if day_schedules
               for day_schedule in day_schedules if day_schedule.lessons)
