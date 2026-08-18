from itertools import chain

from schedule_db_models import LessonORM
from sqlalchemy import ScalarResult, select

from service_parser.infrastructure.domain_mappers import (
    lessons_orm_to_day_schedule_domain,
)
from tests.test_contains import (
    _DAY_SCHEDULE,
    _DAY_SCHEDULE_TO_REPLACE,
    _GROUP_ITEM,
    _GROUP_NUMBER,
    _SCHEDULE_DATE,
    _SCHEDULE_LESSON_ITEMS,
    _SCHEDULE_LESSON_TO_REPLACE_ITEMS,
)


# ===================== [ТЕСТЫ МЕТОДА SAVE] =====================
async def test_save_schedule(
    sqlalchemy_group_repo,
    sqlalchemy_cabinet_repo,
    sqlalchemy_schedule_repo,
    sqlalchemy_session,
):
    """Тест должен корректно сохранить сущность DaySchedule в базу данных"""
    await sqlalchemy_group_repo.save([_GROUP_ITEM])
    await sqlalchemy_cabinet_repo.save(
        {
            cabinet
            for lesson in _SCHEDULE_LESSON_ITEMS
            if lesson.cabinets
            for cabinet in lesson.cabinets
        }
    )

    await sqlalchemy_schedule_repo.save([_DAY_SCHEDULE], _SCHEDULE_DATE)

    stmt = (
        select(LessonORM)
        .where(
            LessonORM.group_index == _GROUP_ITEM.index, LessonORM.date == _SCHEDULE_DATE
        )
        .order_by(LessonORM.start)
    )
    lessons: ScalarResult[LessonORM] = await sqlalchemy_session.scalars(stmt)
    day_schedule = lessons_orm_to_day_schedule_domain(lessons, check_redirect=False)

    assert day_schedule is not None
    assert day_schedule.group.number == _GROUP_NUMBER
    assert day_schedule.lessons == tuple(_SCHEDULE_LESSON_ITEMS)


async def test_save_schedule_with_rewrite(
    sqlalchemy_group_repo,
    sqlalchemy_cabinet_repo,
    sqlalchemy_schedule_repo,
    sqlalchemy_session,
):
    """
    Тест должен корректно сохранить сущность DaySchedule в базу данных
    с удалением лишних записей
    """
    await sqlalchemy_group_repo.save([_GROUP_ITEM])
    await sqlalchemy_cabinet_repo.save(
        {
            cabinet
            for lesson in chain.from_iterable(
                [_SCHEDULE_LESSON_ITEMS, _SCHEDULE_LESSON_TO_REPLACE_ITEMS]
            )
            if lesson.cabinets
            for cabinet in lesson.cabinets
        }
    )

    await sqlalchemy_schedule_repo.save([_DAY_SCHEDULE], _SCHEDULE_DATE)

    await sqlalchemy_schedule_repo.save([_DAY_SCHEDULE_TO_REPLACE], _SCHEDULE_DATE)

    stmt = (
        select(LessonORM)
        .where(
            LessonORM.group_index == _GROUP_ITEM.index, LessonORM.date == _SCHEDULE_DATE
        )
        .order_by(LessonORM.start)
    )
    lessons: ScalarResult[LessonORM] = await sqlalchemy_session.scalars(stmt)
    day_schedule = lessons_orm_to_day_schedule_domain(lessons, check_redirect=False)

    assert day_schedule is not None
    assert day_schedule.group.number == _GROUP_NUMBER
    assert day_schedule.lessons == tuple(_SCHEDULE_LESSON_TO_REPLACE_ITEMS)
