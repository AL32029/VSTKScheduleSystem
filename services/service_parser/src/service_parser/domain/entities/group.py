from dataclasses import dataclass

from patterns import GROUP_NUMBER, ITEM_INDEX

from service_parser.domain.exceptions import (
    GroupNumberFormatError,
    GroupParserPositionError,
)


@dataclass(frozen=True)
class Group:
    index: str
    number: str

    def __init__(self, number: str):
        _number = number.upper().strip()

        if not GROUP_NUMBER.match(_number):
            raise GroupNumberFormatError(f"Invalid group number: {number!r}")

        object.__setattr__(self, "index", ITEM_INDEX.sub("", _number.lower()))
        object.__setattr__(self, "number", _number)

    def __eq__(self, other):
        if not isinstance(other, Group):
            raise NotImplementedError

        return self.index == other.index

    def __hash__(self):
        return hash(self.index)

    def __str__(self):
        return self.number


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
