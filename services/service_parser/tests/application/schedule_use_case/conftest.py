import pytest

from service_parser.application.services.schedule_use_case import CreateDayScheduleUseCase, GetDayScheduleByGroupUseCase


@pytest.fixture
async def create_day_schedule_use_case(schedule_repository) -> CreateDayScheduleUseCase:
    return CreateDayScheduleUseCase(schedule_repository)


@pytest.fixture
async def get_day_schedule_by_group_use_case(schedule_repository) -> GetDayScheduleByGroupUseCase:
    return GetDayScheduleByGroupUseCase(schedule_repository)
