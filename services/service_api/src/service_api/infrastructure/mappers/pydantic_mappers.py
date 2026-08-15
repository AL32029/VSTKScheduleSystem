from collections.abc import Iterable

from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    Group,
    GroupDaySchedule,
)
from service_api.infrastructure.pydantic_schemas import (
    APISchemas,
    CabinetDayScheduleSchema,
    CabinetLessonSchema,
    GroupDayScheduleSchema,
    GroupLessonSchema,
    ResponseSchema,
    ScheduleItemSchema,
)


def schedule_domain_to_schema(schedule_item: "Group | Cabinet") -> "ScheduleItemSchema":
    return ScheduleItemSchema(index=schedule_item.index, number=schedule_item.number)


def group_day_schedule_to_schema(
    day_schedule: "GroupDaySchedule",
) -> "GroupDayScheduleSchema":
    return GroupDayScheduleSchema(
        group=schedule_domain_to_schema(day_schedule.group),
        date=day_schedule.date,
        lessons=[
            GroupLessonSchema(
                start=lesson.start,
                end=lesson.end,
                name=lesson.name,
                cabinets=[
                    schedule_domain_to_schema(cabinet) for cabinet in lesson.cabinets
                ],
            )
            for lesson in day_schedule.lessons
        ],
    )


def cabinet_day_schedule_to_schema(
    day_schedule: "CabinetDaySchedule",
) -> "CabinetDayScheduleSchema":
    return CabinetDayScheduleSchema(
        cabinet=schedule_domain_to_schema(day_schedule.cabinet),
        date=day_schedule.date,
        lessons=[
            CabinetLessonSchema(
                start=lesson.start,
                end=lesson.end,
                group=schedule_domain_to_schema(lesson.group),
                name=lesson.name,
                cabinets=[
                    schedule_domain_to_schema(cabinet) for cabinet in lesson.cabinets
                ],
            )
            for lesson in day_schedule.lessons
        ],
    )


def schedule_item_schema_to_response(
    data: "APISchemas | Iterable[APISchemas]",
) -> "ResponseSchema":
    return ResponseSchema(data=data)
