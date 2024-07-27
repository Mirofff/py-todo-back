import typing as t
import uuid

from src.types import abstract as abstract_types

_T = t.TypeVar("_T", bound=abstract_types.AbstractDomainModel)


class ModelItemNotFound(Exception, t.Generic[_T]):
    def __init__(self, id_: uuid.UUID):
        self.message = f"Item of {_T.__class__.__name__} with {id_=} not found!"
        super().__init__(self.message)
