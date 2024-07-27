import typing as t
import uuid

import pydantic

from ._base import FromAttributesBaseModel


class Task(FromAttributesBaseModel):
    id_: uuid.UUID = pydantic.Field(uuid.UUID, serialization_alias="id")
    title: str
    description: str
    is_done: bool = pydantic.Field(bool, serialization_alias="isDone")
    tags: t.Sequence[str]


class TaskCreate(FromAttributesBaseModel):
    title: str
    description: str
    tags: t.Sequence[str]
    is_done: bool = pydantic.Field(bool, alias="isDone")


class TaskUpdate(FromAttributesBaseModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = pydantic.Field(None, alias="isDone")
    tags: t.Sequence[str] | None = None
