from dataclasses import dataclass


@dataclass(frozen=True)
class Group:
    """Сущность группы"""
    index: str
    number: str

    def __str__(self):
        return self.number

    def __hash__(self):
        return hash(self.index)

    def __eq__(self, other):
        if not isinstance(other, Group):
            raise NotImplementedError

        return self.index == other.index
