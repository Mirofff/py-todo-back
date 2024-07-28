import typing as t

import pydantic

from packages import common as common_packages
from src.types import dynamo as dynamo_types

from ._base import FromAttributesBaseModel

_T = t.TypeVar("_T", bound=pydantic.BaseModel)


class DataPageInfo(FromAttributesBaseModel):
    pagesize: int
    next_page: dynamo_types.DynoItem | None = pydantic.Field(exclude=True)

    @pydantic.computed_field
    @property
    def next_token(self) -> str | None:
        if self.next_page is not None:
            return common_packages.python_to_base64(self.next_page)


class DataPage(FromAttributesBaseModel, t.Generic[_T]):
    items: t.Sequence[_T]
    info: DataPageInfo
