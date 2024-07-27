import typing as t
import abc
import attr


@attr.s(slots=True)
class AbstractDomainModel(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def create(cls, *args, **kwargs) -> t.Self: ...

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__slots__}

    def update(self, **kwargs):
        for slot in self.__slots__:
            if kwargs.get(slot) is not None:
                setattr(self, slot, kwargs[slot])

    def __repr__(self) -> str:
        items = {k: getattr(self, k) for k in self.__slots__}
        return f"{self.__class__.__name__}: {items}"
