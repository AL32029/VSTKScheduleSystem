import datetime
import re
from collections import defaultdict
from typing import Any, Literal

import numpy
from bs4 import BeautifulSoup
from httpx import AsyncClient
from numpy import vectorize, argwhere, ndarray, dtype

from service_parser.application.ports.schedule_provider import ScheduleProvider
from service_parser.domain.entities import DaySchedule, Group, GroupParser, Lesson, Cabinet
from service_parser.domain.shared.patterns import CABINET_NUMBER


class HTTPXScheduleProvider(ScheduleProvider):
    _DATE_WORD_PATTERN = re.compile(r'((\d{2})\s*+([а-я]+)\s*+(\d{4}))')
    _DATE_NUMBERED_PATTERN = re.compile(r'((\d{2}).(\d{2}).(\d{4}))')
    _LESSONS_TIME_PATTERN = re.compile(r'^(\d{1,2})[.:](\d{1,2})\s*[—\-–−-]\s*(\d{1,2})[.:](\d{1,2})$')

    _MONTH_TO_NUMBER = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12
    }

    def __init__(self, client: AsyncClient, schedule_type: Literal['today', 'tomorrow']):
        self.client = client
        self.schedule_type = schedule_type

    async def get_schedule_for_groups(self, url: str) -> dict[Group, tuple[DaySchedule, ...]]:
        # TODO: Реализовать кастомную ошибку при некорректном парсинге (return {})
        html = await self._fetch_html(url)

        table = self._fetch_table(html)

        if table is None:
            return {}

        matrix = self._parse_table_to_matrix(table)

        if matrix is None:
            return {}

        date_list = self._extract_dates(matrix)

        if date_list is None:
            return {}

        lessons_time = self._extract_times(matrix)

        if lessons_time is None:
            return {}

        groups = self._extract_groups(matrix)

        if groups is None:
            return {}

        group_lessons = self._extract_lessons(matrix, date_list, lessons_time, groups)

        return group_lessons

    async def _fetch_html(self, url: str) -> str:
        response = await self.client.get(url)

        response.raise_for_status()

        return response.text

    @staticmethod
    def _fetch_table(html: str) -> BeautifulSoup | None:
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table', class_='excel')

        if not table:
            return None

        return table

    @staticmethod
    def _parse_table_to_matrix(table: BeautifulSoup) -> ndarray[tuple[int, int], dtype[Any]] | None:
        rows_raw = [tr.find_all('td') for tr in table.find_all('tr')]
        rows_count = len(rows_raw)
        if rows_count == 0:
            return None

        max_cols = 0
        rows = []

        for row in rows_raw:
            row_data = []
            row_cols = 0
            for cell in row:
                colspan = int(cell.get('colspan', '1'))
                rowspan = int(cell.get('rowspan', '1'))
                text = cell.text or None
                row_data.append((text, rowspan, colspan))
                row_cols += colspan
            rows.append(row_data)
            if row_cols > max_cols:
                max_cols = row_cols

        matrix = numpy.full((rows_count, max_cols), None, dtype=object)

        for r_idx, row_data in enumerate(rows):
            c_idx = 0
            for text, rowspan, colspan in row_data:
                while c_idx < max_cols and matrix[r_idx][c_idx] is not None:
                    c_idx += 1
                if c_idx + colspan > max_cols or r_idx + rowspan > rows_count:
                    continue
                matrix[r_idx:r_idx + rowspan, c_idx:c_idx + colspan] = text
                c_idx += colspan

        return matrix

    def _extract_dates(self, matrix: ndarray[tuple[int, int], dtype[Any]]) -> tuple[datetime.date, ...] | None:
        match_func = vectorize(lambda s: s and bool(
            self._DATE_WORD_PATTERN.findall(s) or self._DATE_NUMBERED_PATTERN.findall(s)
        ))

        mask = match_func(matrix)

        if not (matrix_mask := matrix[mask]).all():
            return None

        date_list: list[datetime.date] = []

        for m_mask in matrix_mask:
            if date := self._DATE_WORD_PATTERN.findall(m_mask):
                for d in date:
                    date_list.append(datetime.date(
                        day=int(d[1]), month=int(self._MONTH_TO_NUMBER[d[2]]), year=int(d[3])
                    ))

            if date := self._DATE_NUMBERED_PATTERN.findall(m_mask):
                for d in date:
                    date_list.append(datetime.date(day=int(d[1]), month=int(d[2]), year=int(d[3])))

        if not date_list:
            return None

        date_list = list(sorted(date_list, key=lambda x: x))

        date_full_list = [
            date_list[0] + datetime.timedelta(days=i)
            for i in range((date_list[-1] - date_list[0]).days + 1)
        ]

        today = datetime.date.today()

        date_list = list(filter(
            lambda x: x and ((x == today) if self.schedule_type == 'today' else (x > today)),
            date_full_list
        ))

        if not date_list:
            return None

        return tuple(date_list)

    def _extract_times(
            self, matrix: ndarray[tuple[int, int], dtype[Any]]
    ) -> tuple[tuple[datetime.time, datetime.time], ...] | None:
        match_func = vectorize(lambda s: s and bool(self._LESSONS_TIME_PATTERN.match(s)))

        mask = match_func(matrix)

        if not (matrix_mask := matrix[mask]).all():
            return None

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

        if not lessons_time:
            return None

        return tuple(sorted(lessons_time, key=lambda x: x[0]))

    @staticmethod
    def _extract_groups(matrix: ndarray[tuple[int, int], dtype[Any]]) -> tuple[GroupParser, ...] | None:
        match_func = vectorize(lambda s: s and bool(CABINET_NUMBER.match(s)))

        mask = match_func(matrix)

        if not (matrix_mask := matrix[mask]).all():
            return None

        groups = list(GroupParser(group=g, pos_x=int(x), pos_y=int(y)) for g, (y, x) in zip(matrix_mask, argwhere(mask)))

        return tuple(sorted(groups, key=lambda x: x.group.index))

    def _extract_lessons(self, matrix: ndarray[tuple[int, int], dtype[Any]], date_list: tuple[datetime.date, ...],
                         lessons_time: tuple[tuple[datetime.time, datetime.time], ...],
                         groups: tuple[GroupParser, ...]) -> dict[Group, tuple[DaySchedule, ...]]:
        group_lessons: dict[Group, list[DaySchedule]] = defaultdict(list[DaySchedule])

        lessons_count = len(lessons_time)

        for group in groups:
            lessons: list[Lesson] = []
            for l_idx, (lesson, cabinets) in enumerate(
                    matrix[group.pos_y + 1:group.pos_y + lessons_count + 1,
                    group.pos_x:group.pos_x + 2]
            ):
                if group.group in group_lessons and lesson is None:
                    break

                if lessons and (lesson is None or not lesson.strip()):
                    break

                if lesson is None or not lesson.strip():
                    continue

                if not self._LESSONS_TIME_PATTERN.match(matrix[group.pos_y + l_idx + 1, 1]):
                    break

                cabinets = tuple(cabinets.split('/')) if cabinets else tuple()

                lessons.append(Lesson(
                    start=lessons_time[l_idx][0],
                    end=lessons_time[l_idx][1],
                    name=lesson,
                    cabinets=tuple(Cabinet(cab) for cab in cabinets)
                ))

            if lessons:
                group_lessons[group.group].extend([
                    DaySchedule.from_existing(date, group.group, sorted(lessons, key=lambda x: x.start))
                    for date in date_list
                ])

        if not group_lessons:
            return {}

        lessons_return: dict[Group, tuple[DaySchedule, ...]] = {
            k: tuple(sorted(v, key=lambda x: x.date))
            for k, v in group_lessons.items()
        }

        return lessons_return
