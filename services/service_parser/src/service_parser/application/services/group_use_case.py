from typing import Iterable

from service_parser.application.ports import GroupRepository
from service_parser.domain.entities import Group


def _get_group_model(group: str | Group) -> Group:
    return group if isinstance(group, Group) else Group(group)


class GroupUseCase:
    def __init__(self, group_repo: GroupRepository):
        self.repo = group_repo


class CreateGroupUseCase(GroupUseCase):
    async def execute(self, group: str | Group) -> Group:
        group_model = _get_group_model(group)

        await self.repo.save(group_model)

        return group_model


class DeleteGroupUseCase(GroupUseCase):
    async def execute(self, group: str | Group) -> None:
        await self.repo.delete(_get_group_model(group))


class GetGroupByIndexUseCase(GroupUseCase):
    async def execute(self, group: str | Group) -> Group:
        group_db = await self.repo.get_by_index(_get_group_model(group).index)

        return group_db


class GetAllGroupsUseCase(GroupUseCase):
    async def execute(self) -> Iterable[Group]:
        groups = await self.repo.get_all()

        return groups
