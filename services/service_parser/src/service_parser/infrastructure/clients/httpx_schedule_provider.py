import datetime
import hashlib
import re
from collections import defaultdict
from re import Pattern
from typing import Any, ClassVar, Literal
from zoneinfo import ZoneInfo

import numpy
from bs4 import BeautifulSoup
from httpx import AsyncClient
from numpy import argwhere, dtype, ndarray, vectorize
from patterns import CABINET_NUMBER
from redis.asyncio import Redis

from service_parser.application.ports import ScheduleProvider
from service_parser.domain.entities import (
    Cabinet,
    DaySchedule,
    Group,
    GroupParser,
    Lesson,
)
from service_parser.domain.exceptions import (
    FetchingTableError,
    ParsingDateError,
    ParsingDayScheduleError,
    ParsingGroupsError,
    ParsingLessonTimesError,
    ParsingMatrixError,
    ScheduleUnchangedError,
)


class HTTPXScheduleProvider(ScheduleProvider):
    _DATE_WORD_PATTERN: ClassVar[Pattern] = re.compile(
        r"((\d{2})\s*+([а-я]+)\s*+(\d{4}))"
    )
    _DATE_NUMBERED_PATTERN: ClassVar[Pattern] = re.compile(r"((\d{2}).(\d{2}).(\d{4}))")
    _LESSONS_TIME_PATTERN: ClassVar[Pattern] = re.compile(
        r"^(\d{1,2})[.:](\d{1,2})\s*[—\-–−-]"
        r"\s*(\d{1,2})[.:](\d{1,2})$"
    )
    _SCHEDULE_SITE_URL: ClassVar[str] = (
        "https://vgtk.by/schedule/lessons/day-{schedule_type}.php"
    )

    _MONTH_TO_NUMBER: ClassVar[dict] = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12,
    }

    def __init__(
        self,
        client: AsyncClient,
        redis_client: Redis,
        timezone: ZoneInfo,
        schedule_type: Literal["today", "tomorrow"],
    ):
        self.client = client
        self.redis_client = redis_client
        self.timezone = timezone
        self.schedule_type = schedule_type

    async def get_schedule_for_groups(self) -> dict["Group", list["DaySchedule"]]:
        html = await self._fetch_html(
            self._SCHEDULE_SITE_URL.format(schedule_type=self.schedule_type)
        )

        table = self._fetch_table(html)

        table_hash = hashlib.md5(str(table).encode("utf-8")).hexdigest()

        matrix = self._parse_table_to_matrix(table)

        date_list = self._extract_dates(matrix)

        dates_hash = hashlib.md5(str(date_list).encode("utf-8")).hexdigest()

        check_hash = hashlib.md5(
            table_hash.encode("utf-8") + dates_hash.encode("utf-8")
        ).hexdigest()

        redis_key = f"schedule_table:hash:{self.schedule_type}"

        redis_hash = await self.redis_client.get(redis_key)

        if redis_hash:
            cached_hash = redis_hash.decode("utf-8")
            if cached_hash == check_hash:
                raise ScheduleUnchangedError(
                    "The schedule has not changed since the last check"
                )

        await self.redis_client.set(redis_key, check_hash, ex=432000)

        lessons_time = self._extract_times(matrix)

        groups = self._extract_groups(matrix)

        group_lessons = self._extract_lessons(matrix, date_list, lessons_time, groups)

        return group_lessons

    async def _fetch_html(self, url: str) -> str:
        response = await self.client.get(url)

        response.raise_for_status()

        return response.text

    @staticmethod
    def _fetch_table(html: str) -> "BeautifulSoup":
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", class_="excel")

        if not table:
            raise FetchingTableError(
                f"The HTML content does not contain a <table> "
                f"with the class {'excel'!r}"
            )

        return table

    @staticmethod
    def _parse_table_to_matrix(
        table: "BeautifulSoup",
    ) -> ndarray[tuple[int, int], dtype[Any]]:
        rows_raw = [tr.find_all("td") for tr in table.find_all("tr")]
        rows_count = len(rows_raw)
        if rows_count == 0:
            raise ParsingMatrixError("The schedule table does not contain any rows")

        max_cols = 0
        rows = []

        for row in rows_raw:
            row_data = []
            row_cols = 0
            for cell in row:
                colspan = int(cell.get("colspan", "1"))
                rowspan = int(cell.get("rowspan", "1"))
                text = cell.text or ""
                row_data.append((text, rowspan, colspan))
                row_cols += colspan
            rows.append(row_data)
            max_cols = max(max_cols, row_cols)

        if max_cols == 0:
            raise ParsingMatrixError("The schedule table does not contain any columns")

        matrix = numpy.full((rows_count, max_cols), None, dtype=object)

        for r_idx, row_data in enumerate(rows):
            c_idx = 0
            for text, rowspan, colspan in row_data:
                while c_idx < max_cols and matrix[r_idx][c_idx] is not None:
                    c_idx += 1
                if c_idx + colspan > max_cols or r_idx + rowspan > rows_count:
                    continue
                matrix[r_idx : r_idx + rowspan, c_idx : c_idx + colspan] = text
                c_idx += colspan

        return matrix

    def _extract_dates(
        self, matrix: ndarray[tuple[int, int], dtype[Any]]
    ) -> tuple[datetime.date, ...]:
        match_func = vectorize(
            lambda s: (
                s
                and bool(
                    self._DATE_WORD_PATTERN.findall(s)
                    or self._DATE_NUMBERED_PATTERN.findall(s)
                )
            )
        )

        mask = match_func(matrix)

        if not (matrix_mask := matrix[mask]).any():
            raise ParsingDateError(
                "The schedule table does not contain a schedule date "
                "with a predefined format"
            )

        date_list: list[datetime.date] = []

        for m_mask in matrix_mask:
            if date := self._DATE_WORD_PATTERN.findall(m_mask):
                for d in date:
                    date_list.append(
                        datetime.date(
                            day=int(d[1]),
                            month=int(self._MONTH_TO_NUMBER[d[2]]),
                            year=int(d[3]),
                        )
                    )

            if date := self._DATE_NUMBERED_PATTERN.findall(m_mask):
                for d in date:
                    date_list.append(
                        datetime.date(day=int(d[1]), month=int(d[2]), year=int(d[3]))
                    )

        date_list = sorted(date_list, key=lambda x: x)

        date_full_list = [
            date_list[0] + datetime.timedelta(days=i)
            for i in range((date_list[-1] - date_list[0]).days + 1)
        ]

        today = datetime.datetime.now(self.timezone).date()

        date_list = list(
            filter(
                lambda x: (
                    x
                    and ((x == today) if self.schedule_type == "today" else (x > today))
                ),
                date_full_list,
            )
        )

        if not date_list:
            raise ParsingDateError(
                "The schedule table does not contain the schedule date after "
                "checking the items for date compliance"
            )

        return tuple(date_list)

    def _extract_times(
        self, matrix: ndarray[tuple[int, int], dtype[Any]]
    ) -> tuple[tuple[datetime.time, datetime.time], ...]:
        match_func = vectorize(
            lambda s: s and bool(self._LESSONS_TIME_PATTERN.match(s))
        )

        mask = match_func(matrix)

        if not (matrix_mask := matrix[mask]).any():
            raise ParsingLessonTimesError(
                "The schedule table does not contain pairs with a predefined format"
            )

        lessons_time = []

        for l_t in matrix_mask:
            match = self._LESSONS_TIME_PATTERN.match(l_t)

            time_item = (
                datetime.time(hour=int(match.group(1)), minute=int(match.group(2))),
                datetime.time(hour=int(match.group(3)), minute=int(match.group(4))),
            )

            if time_item in lessons_time:
                break

            lessons_time.append(time_item)

        return tuple(sorted(lessons_time, key=lambda x: x[0]))

    @staticmethod
    def _extract_groups(
        matrix: ndarray[tuple[int, int], dtype[Any]],
    ) -> tuple["GroupParser", ...]:
        match_func = vectorize(lambda s: s and bool(CABINET_NUMBER.match(s)))

        mask = match_func(matrix)

        if not (matrix_mask := matrix[mask]).any():
            raise ParsingGroupsError(
                "The schedule table does not contain groups with a predefined format"
            )

        groups = [
            GroupParser(group=g, pos_x=int(x), pos_y=int(y))
            for g, (y, x) in zip(matrix_mask, argwhere(mask), strict=False)
        ]

        return tuple(sorted(groups, key=lambda x: x.group.index))

    def _extract_lessons(  # noqa: C901
        self,
        matrix: ndarray[tuple[int, int], dtype[Any]],
        date_list: tuple[datetime.date, ...],
        lessons_time: tuple[tuple[datetime.time, datetime.time], ...],
        groups: tuple["GroupParser", ...],
    ) -> dict["Group", list["DaySchedule"]]:
        group_lessons: dict[Group, list[DaySchedule]] = defaultdict(list["DaySchedule"])

        lessons_count = len(lessons_time)

        for group in groups:
            lessons: list[Lesson] = []
            for l_idx, (lesson, cabinets) in enumerate(
                matrix[
                    group.pos_y + 1 : group.pos_y + lessons_count,
                    group.pos_x : group.pos_x + 2,
                ]
            ):
                if group.group in group_lessons and lesson is None:
                    break

                if lessons and (lesson is None or not lesson.strip()):
                    break

                if lesson is None or not lesson.strip():
                    continue

                if not self._LESSONS_TIME_PATTERN.match(
                    matrix[group.pos_y + 1 + l_idx, 1]
                ):
                    break

                cabinets = tuple(cabinets.split("/")) if cabinets else ()

                lessons.append(
                    Lesson(
                        start=lessons_time[l_idx][0],
                        end=lessons_time[l_idx][1],
                        name=lesson,
                        cabinets=tuple(Cabinet(cab) for cab in cabinets),
                    )
                )
            if lessons:
                while lessons and lessons[-1].name.lower() == "обед":
                    lessons.pop()

                while lessons and lessons[0].name.lower() == "обед":
                    lessons.pop(0)

                if not lessons:
                    continue

                group_lessons[group.group].extend(
                    [
                        DaySchedule.from_existing(
                            date, group.group, sorted(lessons, key=lambda x: x.start)
                        )
                        for date in date_list
                    ]
                )

        if not group_lessons:
            raise ParsingDayScheduleError(
                "The schedule table does not contain any pairs"
            )

        return group_lessons
