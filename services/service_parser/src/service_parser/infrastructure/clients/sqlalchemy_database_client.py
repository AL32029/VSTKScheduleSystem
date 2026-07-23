import datetime
from dataclasses import replace
from itertools import chain, batched

from schedule_db_models.models import GroupORM, CabinetORM, LessonORM, LessonCabinetORM
from service_parser.application.ports.database_client import DatabaseClient
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from service_parser.domain.entities import Group, Cabinet, Lesson
from service_parser.infrastructure.db.mappers import group_orm_to_domain, cabinet_orm_to_domain, \
    lessons_orm_to_day_schedule_domain, \
    day_schedule_domain_to_lessons_orm


class SQLAlchemyDatabaseClient(DatabaseClient):
    async def check_groups_update(self, groups: list[Group],
                                  session: AsyncSession) -> dict[str, set[Group] | dict[str, set[Group]]]:
        group_stream = await session.stream_scalars(select(GroupORM))

        groups_db: set[Group] = {
            group_orm_to_domain(g)
            async for g in group_stream
        }

        groups_parser: set[Group] = set(groups)

        return {
            'source_data': {
                'schedule': groups_parser,
                'database': groups_db
            },
            'add': groups_parser - groups_db,
            'remove': groups_db - groups_parser
        }

    async def check_cabinets_update(self, cabinets: list[Cabinet],
                                    session: AsyncSession) -> dict[str, set[Cabinet] | dict[str, set[Cabinet]]]:
        cabinets_stream = await session.stream_scalars(select(CabinetORM))

        cabinets_db: set[Cabinet] = {
            cabinet_orm_to_domain(g)
            async for g in cabinets_stream
        }

        cabinets_parser: set[Cabinet] = set(cabinets)

        return {
            'source_data': {
                'schedule': cabinets_parser,
                'database': cabinets_db
            },
            'add': cabinets_parser - cabinets_db
        }

    async def check_lessons_update(
            self, lessons: dict[Group, set[Lesson]], schedule_date: datetime.date, session: AsyncSession
    ) -> dict[str, set[Lesson] | dict[str, set[Lesson]]]:
        lessons_stream = await session.stream_scalars(
            select(LessonORM).
            where(LessonORM.date == schedule_date)
        )

        lessons_db: set[Lesson] = {
            lessons_orm_to_day_schedule_domain(g)
            async for g in lessons_stream
        }

        lessons_parser: set[Lesson] = set(chain.from_iterable(lessons.values()))

        return {
            'source_data': {
                'parser': lessons_parser,
                'database': lessons_db
            },
            'add': lessons_parser - lessons_db,
            'remove': lessons_db - lessons_parser
        }

    async def check_lesson_subjects_update(
            self, lessons: dict, schedule_date: datetime.date
    ) -> dict:
        new_lessons = lessons['source_data']['parser']
        db_lessons = lessons['source_data']['database']

        parser_groups = {lesson._group for lesson in new_lessons}
        db_groups = {lesson._group for lesson in db_lessons}
        add_groups = {lesson._group for lesson in lessons['add']}
        remove_groups = {lesson._group for lesson in lessons['remove']}
        changed_groups = add_groups | remove_groups

        parser_cabinets = {
            cabinet for lesson in new_lessons if lesson.cabinets for cabinet in lesson.cabinets
        }
        db_cabinets = {
            cabinet for lesson in db_lessons if lesson.cabinets for cabinet in lesson.cabinets
        }
        changed_cabinets = {
            cabinet for lesson in chain(lessons['add'], lessons['remove'])
            if lesson.cabinets for cabinet in lesson.cabinets
        }

        return {
            'groups': {
                'new': list(parser_groups - db_groups),
                'updated': list(parser_groups & changed_groups),
            },
            'cabinets': {
                'new': list(parser_cabinets - db_cabinets),
                'updated': list(parser_cabinets & changed_cabinets),
            }
        }

    async def submit_groups_update(self, groups: dict[str, set[Group] | dict[str, set[Group]]],
                                   session: AsyncSession, commit: bool = False) -> None:
        if groups['remove']:
            await session.execute(
                delete(GroupORM).
                where(GroupORM.index.in_([g.index for g in groups['remove']]))
            )

        if groups['add']:
            await session.execute(
                insert(GroupORM).
                values([
                    g.__dict__
                    for g in groups['add']
                ])
            )

        if commit:
            await session.commit()

    async def submit_cabinets_update(self, cabinets: set[Cabinet], session: AsyncSession,
                                     commit: bool = False) -> None:
        if cabinets:
            await session.execute(
                insert(CabinetORM).
                values([
                    c.__dict__
                    for c in cabinets
                ])
            )

        if commit:
            await session.commit()

    async def submit_lessons_update(self, lessons: dict[str, set[Lesson] | dict[str, set[Lesson]]],
                                    schedule_dates: list[datetime.date], session: AsyncSession,
                                    commit: bool = False) -> None:
        if lessons['remove']:
            await session.execute(
                delete(LessonORM).
                where(LessonORM.id.in_([lesson.id for lesson in lessons['remove'] if lesson.id]))
            )

        if lessons['add']:
            lessons_add: list[Lesson] = []
            cabinets_add: list[tuple[Cabinet]] = []

            for lesson in lessons['add']:
                for schedule_date in schedule_dates:
                    lesson_to_add = replace(lesson, date=schedule_date)

                    lessons_add.append(lesson_to_add)
                    cabinets_add.append(lesson_to_add.cabinets)

            insert_ids = []

            for lessons in batched(lessons_add, 100):
                lesson_ids = (await session.scalars(
                    insert(LessonORM).
                    values([
                        {
                            k: v
                            for k, v in day_schedule_domain_to_lessons_orm(lesson).__dict__.items()
                            if k not in ['_sa_instance_state', 'cabinet_relationships']
                        }
                        for lesson in lessons
                    ]).
                    returning(LessonORM.id)
                )).all()

                insert_ids.extend(lesson_ids)

            if insert_ids:
                for items in batched(zip(insert_ids, cabinets_add), 400):
                    relationships_add = [
                        {
                            'lesson_id': lesson_id,
                            'cabinet_id': cabinet.index
                        }
                        for lesson_id, cabinets in items if cabinets
                        for cabinet in cabinets
                    ]
                    if relationships_add:
                        await session.execute(
                            insert(LessonCabinetORM).
                            values(relationships_add)
                        )

        if commit:
            await session.commit()
