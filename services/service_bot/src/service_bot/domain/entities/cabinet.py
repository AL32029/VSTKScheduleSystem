from dataclasses import dataclass


@dataclass(frozen=True)
class Cabinet:
    """Сущность кабинета"""
    index: str
    number: str

    def __str__(self):
        return self.number

    def __hash__(self):
        return hash(self.index)

    def __eq__(self, other):
        if not isinstance(other, Cabinet):
            raise NotImplementedError

        return self.index == self.index
