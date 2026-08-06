import datetime
from collections.abc import Iterable

from schedule_db_models import CabinetORM, GroupORM, LessonCabinetORM, LessonORM

from service_parser.domain.entities import Cabinet, DaySchedule, Group, Lesson
from service_parser.domain.exceptions import (
    SavingDayScheduleDateNotFound,
    SavingDayScheduleGroupNotFound,
    ScheduleForSomeDatesError,
    ScheduleForSomeGroupsError,
)


def group_domain_to_orm(group: 'Group') -> 'GroupORM':
    return GroupORM(
        index=group.index,
        number=group.number
    )


def group_orm_to_domain(group: 'GroupORM') -> 'Group':
    return Group(group.number)


def cabinet_domain_to_orm(cabinet: 'Cabinet') -> 'CabinetORM':
    return CabinetORM(
        index=cabinet.index,
        number=cabinet.number
    )


def cabinet_orm_to_domain(cabinet: 'CabinetORM', check_redirect: bool = False) -> 'Cabinet':
    c = cabinet.redirected if check_redirect else cabinet
    return Cabinet(c.number)


def day_schedule_domain_to_lessons_orm(schedule: 'DaySchedule') -> list['LessonORM']:
    return [
        LessonORM(
            group_index=schedule.group.index,
            date=schedule.date,
            start=lesson.start,
            end=lesson.end,
            name=lesson.name,
            cabinet_relationships=[
                LessonCabinetORM(cabinet_id=cabinet.index, cabinet_index=idx)
                for idx, cabinet in enumerate(lesson.cabinets)
            ]
        )
        for lesson in schedule.lessons
    ]


def lesson_orm_to_domain(lesson: 'LessonORM', check_redirect: bool = False) -> 'Lesson':
    cabinets = sorted(
        [(cab.cabinet_index, cab.cabinet_item) for cab in lesson.cabinet_relationships],
        key=lambda x: x[0]
    )

    return Lesson(
        start=lesson.start,
        end=lesson.end,
        name=lesson.name,
        cabinets=tuple(cabinet_orm_to_domain(cab.redirected if check_redirect else cab) for _, cab in cabinets)
    )


def lesson_domain_in_orm(date: datetime.date, group: 'Group', lesson: 'Lesson') -> 'LessonORM':
    return LessonORM(
        group_index=group.index,
        date=date,
        start=lesson.start,
        end=lesson.end,
        name=lesson.name,
        cabinet_relationships=[
            LessonCabinetORM(cabinet_id=cabinet.index, cabinet_index=idx)
            for idx, cabinet in enumerate(lesson.cabinets)
        ]
    )


def lessons_orm_to_day_schedule_domain(schedule: Iterable['LessonORM'], check_redirect: bool = False) -> 'DaySchedule':
    groups_found: set[Group] = set()
    schedule_dates: set[datetime.date] = set()

    schedule_lessons, schedule_group, schedule_date = [], None, None
    for lesson in sorted(schedule, key=lambda x: x.start):
        groups_found.add(group_orm_to_domain(lesson.group))
        schedule_dates.add(lesson.date)

        if schedule_group is None:
            schedule_group = group_orm_to_domain(lesson.group)

        if schedule_date is None:
            schedule_date = lesson.date

        schedule_lessons.append(lesson_orm_to_domain(lesson, check_redirect))

    if schedule_group is None:
        raise SavingDayScheduleGroupNotFound('There is no group in the lessons list')

    if schedule_date is None:
        raise SavingDayScheduleDateNotFound('There is no date in the lessons list')

    if len(groups_found) > 1:
        raise ScheduleForSomeGroupsError(f'The lessons list contains pairs for different '
                                           f'groups: {', '.join(str(group) for group in groups_found)}')

    if len(schedule_dates) > 1:
        raise ScheduleForSomeDatesError(f'The lessons list contains pairs for different dates: '
                                          f'{', '.join(str(schedule_date) for schedule_date in schedule_dates)}')

    return DaySchedule.from_existing(schedule_date, schedule_group, schedule_lessons)
