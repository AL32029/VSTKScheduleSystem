from collections.abc import Iterable

from schedule_db_models import CabinetORM, GroupORM, LessonORM

from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    CabinetLesson,
    Group,
    GroupDaySchedule,
    GroupLesson,
)


# =================== [МАППЕРЫ GROUP] ===================
def group_orm_to_domain(group: GroupORM) -> Group:
    return Group(group.number)


def group_domain_to_orm(group: Group) -> GroupORM:
    return GroupORM(
        index=group.index,
        number=group.number
    )


# =================== [МАППЕРЫ CABINET] ===================
def cabinet_orm_to_domain(cabinet: CabinetORM, redirect: bool = False) -> Cabinet:
    cabinet_result = cabinet.redirected if redirect else cabinet

    return Cabinet(cabinet_result.number)


def cabinet_domain_to_orm(cabinet: Cabinet) -> CabinetORM:
    return CabinetORM(
        index=cabinet.index,
        number=cabinet.number
    )


# =================== [МАППЕРЫ LESSON] ===================
def lesson_orm_to_group_domain(lesson: LessonORM, redirect: bool = False) -> GroupLesson:
    cabinets = [cabinet_orm_to_domain(cabinet)
                for cabinet in (lesson.cabinets_with_redirects if redirect else lesson.cabinets_without_redirects)]

    return GroupLesson(
        start=lesson.start,
        end=lesson.end,
        name=lesson.name,
        cabinets=tuple(cabinets)
    )


def lesson_orm_to_cabinet_domain(lesson: LessonORM, redirect: bool = False):
    cabinets = [cabinet_orm_to_domain(cabinet)
                for cabinet in (lesson.cabinets_with_redirects if redirect else lesson.cabinets_without_redirects)]

    return CabinetLesson(
        start=lesson.start,
        end=lesson.end,
        group=group_orm_to_domain(lesson.group),
        name=lesson.name,
        cabinets=tuple(cabinets)
    )


# =================== [МАППЕРЫ DAYSCHEDULE] ===================
def lessons_orm_to_group_day_schedule_domain(lessons: Iterable[LessonORM], redirect: bool = False) -> GroupDaySchedule:
    dates = tuple({lesson.date
                   for lesson in lessons})

    if len(dates) > 1:
        # TODO: Заменить кастомной ошибкой
        raise ValueError('The provided list of couples contains couples for different days')

    groups = tuple({group_orm_to_domain(lesson.group)
                    for lesson in lessons})

    if len(groups) > 1:
        # TODO: Заменить кастомной ошибкой
        raise ValueError('The provided list of pairs contains pairs for multiple groups')

    return GroupDaySchedule(
        groups[0],
        dates[0],
        tuple(sorted(
            [lesson_orm_to_group_domain(lesson, redirect) for lesson in lessons],
            key=lambda x: x.start
        ))
    )


def lessons_orm_to_cabinet_day_schedule_domain(cabinet: Cabinet, lessons: Iterable[LessonORM],
                                               redirect: bool = False) -> CabinetDaySchedule:
    dates = tuple({lesson.date
                   for lesson in lessons})

    if len(dates) > 1:
        # TODO: Заменить кастомной ошибкой
        raise ValueError('The provided list of couples contains couples for different days')

    lessons_result = [
        lesson_orm_to_cabinet_domain(lesson, redirect)
        for lesson in lessons
        if (cabinets := (lesson.cabinets_with_redirects
                         if redirect else lesson.cabinets_without_redirects))
           and cabinet in {cabinet_orm_to_domain(cabinet_db) for cabinet_db in cabinets}
    ]

    if not lessons_result:
        # TODO: Заменить кастомной ошибкой
        raise ValueError('The provided list of pairs does not contain pairs for the requested room')

    return CabinetDaySchedule(
        cabinet=cabinet,
        date=dates[0],
        lessons=tuple(sorted(lessons_result, key=lambda x: x.start))
    )