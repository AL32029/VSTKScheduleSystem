from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    Group,
    GroupDaySchedule,
)
from service_api.presentation.rest.schemas import (
    CabinetDayScheduleResponse,
    CabinetLessonResponse,
    GroupDayScheduleResponse,
    GroupLessonResponse,
    ScheduleItemResponse,
)


def schedule_domain_to_response(schedule_item: Group | Cabinet) -> ScheduleItemResponse:
    return ScheduleItemResponse(
        index=schedule_item.index,
        number=schedule_item.number
    )


def group_day_schedule_to_response(day_schedule: GroupDaySchedule) -> GroupDayScheduleResponse:
    return GroupDayScheduleResponse(
        group=schedule_domain_to_response(day_schedule.group),
        date=day_schedule.date,
        lessons=[GroupLessonResponse(start=lesson.start, end=lesson.end,
                                     name=lesson.name, cabinets=[schedule_domain_to_response(cabinet)
                                                                 for cabinet in lesson.cabinets])
                 for lesson in day_schedule.lessons],
        lessons_count=day_schedule.lessons_count,
        pairs_count=day_schedule.pairs_count
    )


def cabinet_day_schedule_to_response(day_schedule: CabinetDaySchedule) -> CabinetDayScheduleResponse:
    return CabinetDayScheduleResponse(
        cabinet=schedule_domain_to_response(day_schedule.cabinet),
        date=day_schedule.date,
        lessons=[CabinetLessonResponse(start=lesson.start, end=lesson.end,
                                       group=schedule_domain_to_response(lesson.group), name=lesson.name,
                                       cabinets=[schedule_domain_to_response(cabinet)
                                                 for cabinet in lesson.cabinets])
                 for lesson in day_schedule.lessons],
        lessons_count=day_schedule.lessons_count,
        pairs_count=day_schedule.pairs_count
    )
