from dataclasses import dataclass

from service_parser.domain.shared.patterns import ITEM_INDEX


@dataclass(frozen=True)
class Cabinet:
    index: str
    number: str

    def __init__(self, number: str):
        object.__setattr__(self, 'index', ITEM_INDEX.sub('', number.lower()))
        object.__setattr__(self, 'number', number)

    def __eq__(self, other):
        if not isinstance(other, Cabinet):
            raise NotImplementedError

        return self.index == other.index

    def __hash__(self):
        return hash(self.index)

    def __str__(self):
        return self.number
