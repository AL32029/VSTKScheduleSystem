import datetime
import json
import logging
from collections.abc import Iterable
from dataclasses import asdict
from typing import Literal

from patterns import ITEM_INDEX
from redis.asyncio import Redis

from service_api.application.ports import CacheRepository
from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    Group,
    GroupDaySchedule,
)
from service_api.domain.exceptions import CacheItemNotFound
from service_api.infrastructure.config import system_settings
from service_api.infrastructure.mappers import (
    cabinet_day_schedule_to_schema,
    group_day_schedule_to_schema,
)
from service_api.infrastructure.pydantic_schemas import (
    CabinetDayScheduleSchema,
    GroupDayScheduleSchema,
)

logger = logging.getLogger(__name__)


class RedisCacheRepository(CacheRepository):
    def __init__(self, redis_repo: 'Redis'):
        self.redis_repo = redis_repo

    async def get_group_cache(self, group_number: str) -> 'Group':
        logger.debug('Request HGET group for group %s', group_number)
        group = await self.redis_repo.hget('group', ITEM_INDEX.sub('', group_number.lower()))

        if group is None:
            logger.debug('Group %s not found in cache', group_number)
            raise CacheItemNotFound(f'Cache of group with number {group_number} not found')

        group_item = Group(**json.loads(group))
        logger.debug('Group %s found in cache', group_item.number)
        return group_item

    async def set_group_cache(self, group_item: 'Group', ttl: int = 21600) -> None:
        logger.debug('Saving group %s to cache', group_item.number)
        await self.redis_repo.hset('group', group_item.index,
                                   json.dumps(asdict(group_item), ensure_ascii=False))
        await self.redis_repo.hexpire('group', ttl, group_item.index)
        logger.debug('Group %s saved to cache with TTL %s seconds', group_item.number, ttl)

    async def get_all_groups_cache(self) -> list['Group']:
        logger.debug('Request HGET group field "all" for groups list')
        groups = await self.redis_repo.hget('group', 'all')

        if groups is None:
            logger.debug('Groups list not found in cache')
            raise CacheItemNotFound('Cache of all groups not found')

        group_items = [Group(**group) for group in json.loads(groups)]
        logger.debug('Groups list found in cache, %d items', len(group_items))
        return group_items

    async def set_all_groups_cache(self, group_items: Iterable['Group'], ttl: int = 21600) -> None:
        items = list(group_items)
        items_to_set = {
            'all': json.dumps([asdict(group) for group in items], ensure_ascii=False),
            **{
                group.index: json.dumps(asdict(group), ensure_ascii=False)
                for group in items
            }
        }

        logger.debug('Saving %d groups to cache', len(items))
        await self.redis_repo.hsetex('group', mapping=items_to_set)
        await self.redis_repo.hexpire('group', ttl, *items_to_set.keys())
        logger.debug('%d groups saved to cache with TTL %s seconds', len(items), ttl)

    async def get_cabinet_cache(self, cabinet_number: str) -> 'Cabinet':
        logger.debug('Request HGET cabinet for %s', cabinet_number)
        cabinet = await self.redis_repo.hget('cabinet', ITEM_INDEX.sub('', cabinet_number.lower()))

        if cabinet is None:
            logger.debug('Cabinet %s not found in cache', cabinet_number)
            raise CacheItemNotFound(f'Cache of cabinet with number {cabinet_number} not found')

        logger.debug('Cabinet %s found in cache', cabinet_number)
        return Cabinet(**json.loads(cabinet))

    async def set_cabinet_cache(self, cabinet_item: 'Cabinet', ttl: int = 604800) -> None:
        logger.debug('Saving cabinet %s to cache', cabinet_item.number)
        await self.redis_repo.hset('cabinet', cabinet_item.index,
                                   json.dumps(asdict(cabinet_item), ensure_ascii=False))
        await self.redis_repo.hexpire('cabinet', ttl, cabinet_item.index)
        logger.debug('Cabinet %s saved to cache with TTL %s seconds', cabinet_item.number, ttl)

    async def get_all_cabinets_cache(self) -> list['Cabinet']:
        logger.debug('Request HGET cabinet field "all" for cabinets list')
        cabinets = await self.redis_repo.hget('cabinet', 'all')

        if cabinets is None:
            logger.debug('Cabinets list not found in cache')
            raise CacheItemNotFound('Cache of all cabinets not found')

        result = [Cabinet(**cabinet) for cabinet in json.loads(cabinets)]
        logger.debug('Cabinets list found in cache, %d items', len(result))
        return result

    async def set_all_cabinets_cache(self, cabinet_items: Iterable['Cabinet'], ttl: int = 604800) -> None:
        items = list(cabinet_items)
        items_to_set = {
            'all': json.dumps([asdict(cabinet) for cabinet in items], ensure_ascii=False),
            **{
                cabinet.index: json.dumps(asdict(cabinet), ensure_ascii=False)
                for cabinet in items
            }
        }

        logger.debug('Saving %d cabinets to cache', len(items))
        await self.redis_repo.hsetex('cabinet', mapping=items_to_set)
        await self.redis_repo.hexpire('cabinet', ttl, *items_to_set.keys())
        logger.debug('%d cabinets saved to cache with TTL %s seconds', len(items), ttl)

    async def get_group_day_schedule(self, schedule_to: Literal['today', 'tomorrow'],
                                     group_number: str) -> 'GroupDaySchedule':
        key = f'group:{ITEM_INDEX.sub('', group_number.lower())}:{schedule_to}'
        logger.debug('Request HGET schedule field "%s"', key)
        day_schedule = await self.redis_repo.hget('schedule', key)

        if day_schedule is None:
            logger.debug('Day schedule for group %s (%s) not found in cache', group_number, schedule_to)
            raise CacheItemNotFound(f'Cache of day schedule for {group_number!r} at {schedule_to} not found')

        logger.debug('Day schedule for group %s (%s) found in cache', group_number, schedule_to)
        return GroupDayScheduleSchema.model_validate_json(day_schedule).to_domain()

    async def set_group_day_schedule(self, schedule_to: Literal['today', 'tomorrow'],
                                     day_schedule: 'GroupDaySchedule') -> None:
        logger.debug('Saving group day schedule for %s (%s) to cache', day_schedule.group.number, schedule_to)
        await self.set_group_cache(day_schedule.group)

        cabinets_to_save = {
            cabinet
            for lesson in day_schedule.lessons if lesson.cabinets
            for cabinet in lesson.cabinets
        }
        if cabinets_to_save:
            logger.debug('Additionally saving %d related cabinets for group schedule', len(cabinets_to_save))
            await self.set_all_cabinets_cache(cabinets_to_save)

        field = f'group:{day_schedule.group.index}:{schedule_to}'
        await self.redis_repo.hsetex(
            'schedule',
            field,
            group_day_schedule_to_schema(day_schedule).model_dump_json(ensure_ascii=False)
        )

        ttl = datetime.datetime.now(system_settings.TIMEZONE).replace(hour=23, minute=59, second=59)
        logger.debug('Setting expiration at %s for schedule field "%s"', ttl.isoformat(), field)
        await self.redis_repo.hexpireat('schedule', ttl, field)
        logger.debug('Group day schedule for %s (%s) cached successfully', day_schedule.group.number, schedule_to)

    async def get_cabinet_day_schedule(self, cabinet_number: str,
                                       schedule_to: Literal['today', 'tomorrow']) -> 'CabinetDaySchedule':
        key = f'cabinet:{ITEM_INDEX.sub('', cabinet_number.lower())}:{schedule_to}'
        logger.debug('Request HGET schedule field "%s"', key)
        day_schedule = await self.redis_repo.hget('schedule', key)

        if day_schedule is None:
            logger.debug('Day schedule for cabinet %s (%s) not found in cache', cabinet_number, schedule_to)
            raise CacheItemNotFound(f'Cache of day schedule for {cabinet_number!r} at {schedule_to} not found')

        logger.debug('Day schedule for cabinet %s (%s) found in cache', cabinet_number, schedule_to)
        return CabinetDayScheduleSchema.model_validate_json(day_schedule).to_domain()

    async def set_cabinet_day_schedule(self, schedule_to: Literal['today', 'tomorrow'],
                                       day_schedule: 'CabinetDaySchedule') -> None:
        logger.debug('Saving cabinet day schedule for %s (%s) to cache', day_schedule.cabinet.number, schedule_to)

        groups_to_save = {lesson.group for lesson in day_schedule.lessons}
        if groups_to_save:
            logger.debug('Additionally saving %d related groups for cabinet schedule', len(groups_to_save))
            await self.set_all_groups_cache(groups_to_save)

        cabinets_to_save = {
            cabinet
            for lesson in day_schedule.lessons if lesson.cabinets
            for cabinet in lesson.cabinets
        }
        if cabinets_to_save:
            logger.debug('Additionally saving %d related cabinets for cabinet schedule', len(cabinets_to_save))
            await self.set_all_cabinets_cache(cabinets_to_save)

        field = f'cabinet:{day_schedule.cabinet.index}:{schedule_to}'
        await self.redis_repo.hsetex(
            'schedule',
            field,
            cabinet_day_schedule_to_schema(day_schedule).model_dump_json(ensure_ascii=False)
        )

        ttl = datetime.datetime.now(system_settings.TIMEZONE).replace(hour=23, minute=59, second=59)
        logger.debug('Setting expiration at %s for schedule field "%s"', ttl.isoformat(), field)
        await self.redis_repo.hexpireat('schedule', ttl, field)
        logger.debug('Cabinet day schedule for %s (%s) cached successfully', day_schedule.cabinet.number, schedule_to)
