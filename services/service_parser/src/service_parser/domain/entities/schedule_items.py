from dataclasses import dataclass

from patterns import GROUP_NUMBER, ITEM_INDEX

from service_parser.domain.exceptions import (
    GroupNumberFormatError,
    GroupParserPositionError,
)


class ScheduleItem:
    __slots__ = ("index", "number")

    def __init__(self, number: str):
        index = ITEM_INDEX.sub("", number.lower())
        object.__setattr__(self, "index", index)
        object.__setattr__(self, "number", number)

    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return NotImplemented

        return self.index == other.index

    def __hash__(self) -> int:
        return hash(self.index)

    def __str__(self) -> str:
        return self.number


class Cabinet(ScheduleItem):
    """Сущность кабинета"""


class Group(ScheduleItem):
    """Сущность группы"""

    def __init__(self, number: str):
        _number = number.upper().strip()

        if not GROUP_NUMBER.match(_number):
            raise GroupNumberFormatError(f"Invalid group number: {number!r}")

        super().__init__(_number)


@dataclass(frozen=True)
class GroupParser:
    group: "Group"
    pos_x: int
    pos_y: int

    def __init__(self, group: str, pos_x: int, pos_y: int):
        if pos_x < 0:
            raise GroupParserPositionError("X position must be positive")

        if pos_y < 0:
            raise GroupParserPositionError("Y position must be positive")

        object.__setattr__(self, "group", Group(group))
        object.__setattr__(self, "pos_x", pos_x)
        object.__setattr__(self, "pos_y", pos_y)

    def __eq__(self, other):
        if not isinstance(other, GroupParser):
            raise NotImplementedError

        return (self.group, self.pos_x, self.pos_y) == (
            other.group,
            self.pos_x,
            self.pos_y,
        )

    def __hash__(self):
        return hash((self.group, self.pos_x, self.pos_y))

    def __str__(self):
        return self.group.number
