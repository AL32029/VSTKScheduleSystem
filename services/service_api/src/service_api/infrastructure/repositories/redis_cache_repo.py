import datetime
import json
from collections.abc import Iterable
from dataclasses import asdict
from typing import Literal

from redis.asyncio import Redis

from service_api.application.ports import CacheRepository
from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    Group,
    GroupDaySchedule,
)
from service_api.domain.exceptions import CacheItemNotFound
from service_api.domain.shared.patterns import ITEM_INDEX
from service_api.infrastructure.config import system_settings
from service_api.infrastructure.mappers import (
    cabinet_day_schedule_to_schema,
    group_day_schedule_to_schema,
)
from service_api.infrastructure.pydantic_schemas import (
    CabinetDayScheduleSchema,
    GroupDayScheduleSchema,
)


class RedisCacheRepository(CacheRepository):
    def __init__(self, redis_repo: 'Redis'):
        self.redis_repo = redis_repo

    async def get_group_cache(self, group_number: str) -> 'Group':
        group = await self.redis_repo.hget('group', ITEM_INDEX.sub('', group_number.lower()))

        if group is None:
            raise CacheItemNotFound(f'Cache of group with number {group_number} not found')

        return Group(**json.loads(group))

    async def set_group_cache(self, group_item: 'Group', ttl: int = 21600) -> None:
        await self.redis_repo.hset('group', group_item.index, json.dumps(asdict(group_item), ensure_ascii=False))
        await self.redis_repo.hexpire('group', ttl, group_item.index)

    async def get_all_groups_cache(self) -> list['Group']:
        groups = await self.redis_repo.hget('group', 'all')

        if groups is None:
            raise CacheItemNotFound('Cache of all groups not found')

        return [Group(**group)
                for group in json.loads(groups)]

    async def set_all_groups_cache(self, group_items: Iterable['Group'], ttl: int = 21600) -> None:
        items_to_set = {
            'all': json.dumps([asdict(group) for group in group_items], ensure_ascii=False),
            **{
                group.index: json.dumps(asdict(group), ensure_ascii=False)
                for group in group_items
            }
        }

        await self.redis_repo.hsetex('group', mapping=items_to_set)
        await self.redis_repo.hexpire('group', ttl, *items_to_set.keys())

    async def get_cabinet_cache(self, cabinet_number: str) -> 'Cabinet':
        cabinet = await self.redis_repo.hget('cabinet', ITEM_INDEX.sub('', cabinet_number.lower()))

        if cabinet is None:
            raise CacheItemNotFound(f'Cache of cabinet with number {cabinet_number} not found')

        return Cabinet(**json.loads(cabinet))

    async def set_cabinet_cache(self, cabinet_item: 'Cabinet', ttl: int = 604800) -> None:
        await self.redis_repo.hset('cabinet', cabinet_item.index,
                                   json.dumps(asdict(cabinet_item), ensure_ascii=False))
        await self.redis_repo.hexpire('cabinet', ttl, cabinet_item.index)

    async def get_all_cabinets_cache(self) -> list['Cabinet']:
        cabinets = await self.redis_repo.hget('cabinet', 'all')

        if cabinets is None:
            raise CacheItemNotFound('Cache of all cabinets not found')

        return [Cabinet(**group)
                for group in json.loads(cabinets)]

    async def set_all_cabinets_cache(self, cabinet_items: Iterable['Cabinet'], ttl: int = 604800) -> None:
        items_to_set = {
            'all': json.dumps([asdict(cabinet) for cabinet in cabinet_items], ensure_ascii=False),
            **{
                cabinet.index: json.dumps(asdict(cabinet), ensure_ascii=False)
                for cabinet in cabinet_items
            }
        }

        await self.redis_repo.hsetex('cabinet', mapping=items_to_set)
        await self.redis_repo.hexpire('cabinet', ttl, *items_to_set.keys())

    async def get_group_day_schedule(self, schedule_to: Literal['today', 'tomorrow'],
                                     group_number: str) -> 'GroupDaySchedule':
        day_schedule = await self.redis_repo.hget('schedule',
                                                  f'group:{ITEM_INDEX.sub('', group_number.lower())}:{schedule_to}')

        if day_schedule is None:
            raise CacheItemNotFound(f'Cache of day schedule for {group_number!r} at {schedule_to} not found')

        return GroupDayScheduleSchema.model_validate_json(day_schedule).to_domain()

    async def set_group_day_schedule(self, schedule_to: Literal['today', 'tomorrow'],
                                     day_schedule: 'GroupDaySchedule') -> None:
        await self.set_group_cache(day_schedule.group)

        cabinets_to_save = {cabinet
                            for lesson in day_schedule.lessons if lesson.cabinets
                            for cabinet in lesson.cabinets}
        if cabinets_to_save:
            await self.set_all_cabinets_cache(cabinets_to_save)

        await self.redis_repo.hsetex('schedule', f'group:{day_schedule.group.index}:{schedule_to}',
                                     group_day_schedule_to_schema(day_schedule).model_dump_json(ensure_ascii=False))

        ttl = datetime.datetime.now(system_settings.TIMEZONE).replace(hour=23, minute=59, second=59)

        await self.redis_repo.hexpireat('schedule', ttl,
                                        f'group:{day_schedule.group.index}:{schedule_to}')

    async def get_cabinet_day_schedule(self, cabinet_number: str,
                                       schedule_to: Literal['today', 'tomorrow']) -> 'CabinetDaySchedule':
        day_schedule = await self.redis_repo.hget(
            'schedule',
            f'cabinet:{ITEM_INDEX.sub('', cabinet_number.lower())}:{schedule_to}'
        )

        if day_schedule is None:
            raise CacheItemNotFound(f'Cache of day schedule for {cabinet_number!r} at {schedule_to} not found')

        return CabinetDayScheduleSchema.model_validate(day_schedule).to_domain()

    async def set_cabinet_day_schedule(self, schedule_to: Literal['today', 'tomorrow'],
                                       day_schedule: 'CabinetDaySchedule') -> None:
        groups_to_save = {lesson.group for lesson in day_schedule.lessons}
        if groups_to_save:
            await self.set_all_groups_cache(groups_to_save)

        cabinets_to_save = {cabinet
                            for lesson in day_schedule.lessons if lesson.cabinets
                            for cabinet in lesson.cabinets}
        if cabinets_to_save:
            await self.set_all_cabinets_cache(cabinets_to_save)

        await self.redis_repo.hsetex('schedule', f'cabinet:{day_schedule.cabinet.index}:{schedule_to}',
                                     cabinet_day_schedule_to_schema(day_schedule).model_dump_json(ensure_ascii=False))

        ttl = datetime.datetime.now(system_settings.TIMEZONE).replace(hour=23, minute=59, second=59)

        await self.redis_repo.hexpireat('schedule', ttl,
                                        f'cabinet:{day_schedule.cabinet.index}:{schedule_to}')
