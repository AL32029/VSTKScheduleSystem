from dataclasses import dataclass

from service_api.domain.shared.patterns import ITEM_INDEX


@dataclass(frozen=True)
class Cabinet:
    index: str
    number: str

    def __init__(self, number: str, **kwargs):
        object.__setattr__(self, 'index', kwargs.get('index') or ITEM_INDEX.sub('', number.lower()))
        object.__setattr__(self, 'number', number)

    def __hash__(self):
        return hash(self.index)

    def __eq__(self, other):
        if not isinstance(other, Cabinet):
            raise NotImplementedError

        return self.index == other.index

    def __str__(self):
        return self.number
