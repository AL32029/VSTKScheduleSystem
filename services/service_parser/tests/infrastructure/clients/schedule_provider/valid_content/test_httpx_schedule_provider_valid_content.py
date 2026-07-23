import datetime

from service_parser.domain.entities import GroupParser, DaySchedule


def test_get_schedule_dates(schedule_provider, html_matrix):
    dates = schedule_provider._extract_dates(html_matrix)

    assert dates is not None
    assert len(dates) == 1
    assert dates[0] == datetime.date(2099, 12, 31)


def test_get_lessons_time(schedule_provider, html_matrix):
    lessons_time = schedule_provider._extract_times(html_matrix)

    assert lessons_time is not None
    assert len(lessons_time) == 11
    assert lessons_time == tuple(sorted(lessons_time, key=lambda x: x[0]))
    assert all(isinstance(item, tuple) and len(item) == 2 for item in lessons_time)
    assert all(
        isinstance(start, datetime.time) and isinstance(end, datetime.time)
        for start, end in lessons_time
    )
    assert all(start < end for start, end in lessons_time)

    prev_end_min = None
    for start, end in lessons_time:
        start_min = start.hour * 60 + start.minute
        end_min = end.hour * 60 + end.minute

        if prev_end_min is not None:
            delta = start_min - prev_end_min
            assert delta == 10

        prev_end_min = end_min


def test_get_groups(schedule_provider, html_matrix):
    groups = schedule_provider._extract_groups(html_matrix)

    assert groups is not None
    assert len(groups) == 64
    assert groups == tuple(sorted(groups, key=lambda x: x.group.index))
    assert all(isinstance(item, GroupParser) for item in groups)


def test_get_lessons(schedule_provider, html_matrix):
    date_list = schedule_provider._extract_dates(html_matrix)
    lessons_time = schedule_provider._extract_times(html_matrix)
    groups = schedule_provider._extract_groups(html_matrix)

    lessons = schedule_provider._extract_lessons(html_matrix, date_list, lessons_time, groups)

    assert lessons is not None
    assert len(lessons.keys()) == 64
    assert len(lessons.values()) == 64
    assert all(item.group in lessons for item in groups)
    assert all(
        isinstance(item, tuple) and all(
            isinstance(schedule, DaySchedule)
            and schedule.group == group
            and schedule.date == date_list[0]
            and schedule.lessons == tuple(sorted(schedule.lessons, key=lambda x: x.start))
            for schedule in item
        )
        for group, item in lessons.items()
    )

async def test_get_lessons_for_all_groups(schedule_provider, lessons_extract, httpx_mock):
    with open('./tests/fixtures/schedule.html', 'rb') as f:
        httpx_mock.add_response(
            method='GET',
            url='https://vgtk.by/schedule/lessons/day-tomorrow.php',
            content=f.read()
        )

    lessons = await schedule_provider.get_schedule_for_groups('https://vgtk.by/schedule/lessons/day-tomorrow.php')

    assert lessons is not None
    assert len(lessons.keys()) == 64
    assert len(lessons.values()) == 64
    assert  lessons_extract == lessons