from dataclasses import dataclass


@dataclass(frozen=True)
class Cabinet:
    index: str
    number: str

    def __hash__(self):
        return hash(self.index)

    def __eq__(self, other):
        if not isinstance(other, Cabinet):
            raise NotImplementedError

        return self.index == other.index

    def __str__(self):
        return self.number
