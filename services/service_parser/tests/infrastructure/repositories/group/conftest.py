import pytest

from service_parser.domain.entities import Group


@pytest.fixture
def group_item() -> Group:
    return Group('ЖБИ-21')


@pytest.fixture
async def group_item_saved(group_repository, group_item) -> Group:
    await group_repository.save(group_item)

    return group_item
