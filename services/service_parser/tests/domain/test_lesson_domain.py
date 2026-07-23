import datetime

import pytest

from service_parser.domain.entities import Lesson, Cabinet, Group
from service_parser.domain.entities.lesson import DaySchedule
from service_parser.domain.exceptions import MissingLessonNameError, LessonOverlapError
from service_parser.domain.exceptions.parser_exceptions import InvalidLessonEndTime


@pytest.mark.parametrize('start,end,name,cabinets', [
    [datetime.time(9, 0), datetime.time(9, 45), 'Математика', ('42к',)],
    [datetime.time(9, 55), datetime.time(10, 40), '    Ин. яз.', ('21', '409')],
])
def test_lesson_creation(start: datetime.time, end: datetime.time, name: str, cabinets: tuple[str]):
    """Тест должен создать сущность Lesson"""
    lesson = Lesson(start, end, name, tuple(Cabinet(cab) for cab in cabinets))

    assert isinstance(lesson.start, datetime.time)
    assert lesson.start.hour == start.hour
    assert lesson.start.minute == start.minute

    assert isinstance(lesson.end, datetime.time)
    assert lesson.end.hour == end.hour
    assert lesson.end.minute == end.minute

    assert lesson.name == name.strip()
    assert lesson.cabinets == tuple(Cabinet(cab) if isinstance(cab, str) else cab for cab in cabinets)


@pytest.mark.parametrize('start,end,name,cabinets', [
    [datetime.time(9, 45), datetime.time(9, 0), 'Математика', ('42к',)],
    [datetime.time(10, 40), datetime.time(9, 55), 'Ин. яз.', ('21', '409')],
])
def test_lesson_creation_error_invalid_lesson_end_time(start: datetime.time, end: datetime.time,
                                                       name: str, cabinets: tuple[str]):
    """Тест должен выдать ошибку InvalidLessonEndTime"""
    with pytest.raises(InvalidLessonEndTime) as exc_info:
        Lesson(start=start, end=end, name=name, cabinets=tuple(Cabinet(cabinet) for cabinet in cabinets))

    assert exc_info.value.args[0] == f'End time {str(end)!r} should be greater than start time {str(start)!r}'


@pytest.mark.parametrize('start,end,name,cabinets', [
    [datetime.time(9, 00), datetime.time(9, 45), '', ('42к',)],
    [datetime.time(10, 50), datetime.time(11, 35), '   ', ('сз3',)],
])
def test_lesson_creation_error_missing_lesson_name(start: datetime.time, end: datetime.time,
                                                   name: str, cabinets: tuple[str]):
    """Тест должен выдать ошибку MissingLessonNameError"""
    with pytest.raises(MissingLessonNameError) as exc_info:
        Lesson(start=start, end=end, name=name, cabinets=tuple(Cabinet(cabinet) for cabinet in cabinets))

    assert exc_info.value.args[0] == 'Lesson name is missing'


@pytest.mark.parametrize('start,end,name,cabinets', [
    [datetime.time(9, 0), datetime.time(9, 45), 'Математика', ('42к',)],
    [datetime.time(9, 55), datetime.time(10, 40), 'Ин. яз.', ('21', '409')],
])
def test_lesson_hash(start: datetime.time, end: datetime.time, name: str, cabinets: tuple[str]):
    """Тест должен проверить равенство между двумя хэшами"""
    first_lesson = Lesson(start=start, end=end, name=name, cabinets=tuple(Cabinet(cabinet) for cabinet in cabinets))
    second_lesson = Lesson(start=start, end=end, name=name, cabinets=tuple(Cabinet(cabinet) for cabinet in cabinets))

    assert hash(first_lesson) == hash(second_lesson)
    assert len({first_lesson, second_lesson}) == 1


@pytest.mark.parametrize('group,date', [
    [Group('жби-21'), datetime.date(2026, 7, 20)],
    [Group('ос-21'), datetime.date(2026, 7, 22)],
])
def test_day_schedule_creation(group, date):
    """Тест должен создать агрегат DaySchedule без пар"""
    day_schedule = DaySchedule(date, group)

    assert isinstance(day_schedule.group, Group)
    assert day_schedule.group.number == group.number.upper().strip()

    assert isinstance(day_schedule.date, datetime.date)
    assert day_schedule.date.year == date.year
    assert day_schedule.date.month == date.month
    assert day_schedule.date.day == date.day

    assert not day_schedule.lessons


@pytest.mark.parametrize('group,date,start,end,name,cabinets', [
    [Group('жби-21'), datetime.date(2026, 7, 20), datetime.time(9, 00),
     datetime.time(9, 45), 'Физкультура', ('сз3',)],
    [Group('ос-21'), datetime.date(2026, 7, 22), datetime.time(9, 55),
     datetime.time(10, 40), 'Информатика', ('310', '212')],
])
def test_day_schedule_add_lesson(group: Group, date: datetime.date, start: datetime.time,
                                 end: datetime.time, name: str, cabinets: tuple[str, ...]):
    """Тест должен создать агрегат DaySchedule с имеющейся одной парой"""
    lesson = Lesson(start, end, name, tuple(Cabinet(cab) for cab in cabinets))

    day_schedule = DaySchedule.from_existing(date, group, lessons=[lesson])

    assert len(day_schedule.lessons) == 1
    assert day_schedule.lessons[0] == lesson


@pytest.mark.parametrize('group,date,lesson', [
    [Group('ПЭС-215'), datetime.date(2026, 7, 24),
     Lesson(datetime.time(11, 45), datetime.time(12, 30), 'обед', tuple())],
])
def test_day_schedule_add_lesson_without_cabinets(group: Group, date: datetime.date, lesson: Lesson):
    """Тест должен добавить пару без кабинета"""
    day_schedule = DaySchedule(date, group)

    add_lesson = day_schedule.add_lesson(lesson.start, lesson.end, lesson.name, lesson.cabinets)

    assert isinstance(add_lesson, Lesson)
    assert len(day_schedule.lessons) == 1
    assert day_schedule.lessons[0] == lesson


@pytest.mark.parametrize('group,date,lessons', [
    [Group('ЖБИ-21'), datetime.date(2026, 7, 20), [
        Lesson(datetime.time(9, 0), datetime.time(9, 45), 'Физкультура', (Cabinet('сз3'),)),
        Lesson(datetime.time(9, 55), datetime.time(10, 40), 'Биология', (Cabinet('12к'),)),
        Lesson(datetime.time(10, 50), datetime.time(11, 35), 'Тех. мех', (Cabinet('315'),)),
        Lesson(datetime.time(11, 45), datetime.time(12, 30), 'ОТСМ', (Cabinet('11'),)),
    ]]
])
def test_day_schedule_add_more_lessons(group: Group, date: datetime.date, lessons: list[Lesson]):
    """Тест должен добавить несколько пар"""
    day_schedule = DaySchedule(date, group)

    for lesson in lessons:
        day_schedule.add_lesson(lesson.start, lesson.end, lesson.name, lesson.cabinets)

    assert len(day_schedule.lessons) == 4

    for idx, lesson in enumerate(lessons):
        assert isinstance(lesson, Lesson)
        assert day_schedule.lessons[idx] == lesson


@pytest.mark.parametrize('group,date,lessons', [
    [Group('ЖБИ-21'), datetime.date(2026, 7, 20), [
        Lesson(datetime.time(9, 0), datetime.time(9, 45), 'Физкультура', (Cabinet('сз3'),)),
        Lesson(datetime.time(9, 10), datetime.time(10, 40), 'Биология', (Cabinet('12к'),)),
    ]]
])
def test_day_schedule_add_more_lessons_error_overlap(group: Group, date: datetime.date, lessons: list[Lesson]):
    """Тест должен выдать ошибку LessonOverlapError"""
    day_schedule = DaySchedule(date, group)

    with pytest.raises(LessonOverlapError) as exc_info:
        lesson_add = None
        for lesson in lessons:
            day_schedule.add_lesson(lesson.start, lesson.end, lesson.name, lesson.cabinets)
            lesson_add = day_schedule.lessons[-1]

    assert exc_info.value.args[0] == f'The lesson overlaps with the lesson {lesson_add.name!r} ({str(lesson_add.start)} - {str(lesson_add.end)})'
