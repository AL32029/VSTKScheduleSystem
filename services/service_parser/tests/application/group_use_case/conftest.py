import pytest

from service_parser.application.services.group_use_case import CreateGroupUseCase, DeleteGroupUseCase, \
    GetGroupByIndexUseCase, GetAllGroupsUseCase


@pytest.fixture
async def create_group_use_case(group_repository) -> CreateGroupUseCase:
    return CreateGroupUseCase(group_repository)


@pytest.fixture
async def delete_group_use_case(group_repository) -> DeleteGroupUseCase:
    return DeleteGroupUseCase(group_repository)


@pytest.fixture
async def get_group_by_index_use_case(group_repository) -> GetGroupByIndexUseCase:
    return GetGroupByIndexUseCase(group_repository)


@pytest.fixture
async def get_all_groups_use_case(group_repository) -> GetAllGroupsUseCase:
    return GetAllGroupsUseCase(group_repository)
