import typing as t
import uuid

from src.models import user as user_models
from src.types import abstract as abstract_types


class Task(abstract_types.AbstractDomainModel):
    __slots__ = {"id_", "user_id", "title", "description", "is_done", "tags"}

    def __init__(
        self, id_: uuid.UUID, user_id: uuid.UUID, title: str, description: str, is_done: bool, tags: t.Sequence[str]
    ):
        self.id_ = id_
        self.user_id = user_id
        self.title = title
        self.description = description
        self.is_done = bool(is_done)
        self.tags = tags

    @classmethod
    def create(cls, user: user_models.User, title: str, description: str, tags: t.Sequence[str], is_done: bool):
        return cls(
            id_=uuid.uuid4(),
            user_id=user.id_,
            title=title,
            description=description,
            is_done=is_done,
            tags=[tag.lower() for tag in tags],
        )
