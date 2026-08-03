from dataclasses import dataclass

from service_api.domain.exceptions import GroupNumberFormatError
from service_api.domain.shared.patterns import GROUP_NUMBER, ITEM_INDEX


@dataclass(frozen=True)
class Group:
    index: str
    number: str

    def __init__(self, number: str, **kwargs):
        _number = number.upper().strip()

        if not GROUP_NUMBER.match(_number):
            raise GroupNumberFormatError(f'Invalid group number: {number!r}')

        object.__setattr__(self, 'index', kwargs.get('index') or ITEM_INDEX.sub('', _number.lower()))
        object.__setattr__(self, 'number', _number)

    def __hash__(self):
        return hash(self.index)

    def __eq__(self, other):
        if not isinstance(other, Group):
            raise NotImplementedError

        return self.index == other.index

    def __str__(self):
        return self.number
