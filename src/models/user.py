import uuid

import argon2

from src.types import abstract as abstract_types


class User(abstract_types.AbstractDomainModel):
    __slots__ = {"id_", "email", "first_name", "last_name"}

    def __init__(self, id_: uuid.UUID, email: str, first_name: str, last_name: str) -> None:
        self.id_ = id_
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def create(cls, email: str, first_name: str, last_name: str):
        return cls(id_=uuid.uuid4(), email=email, first_name=first_name, last_name=last_name)


class UserPublic(abstract_types.AbstractDomainModel):
    __slots__ = {"id_", "email", "first_name", "last_name"}

    def __init__(self, id_: uuid.UUID, email: str, first_name: str, last_name: str):
        self.id_ = id_
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def create(cls, email: str, first_name: str, last_name: str):
        return cls(id_=uuid.uuid4(), email=email, first_name=first_name, last_name=last_name)


class UserPassword(abstract_types.AbstractDomainModel):
    __slots__ = {"user_id", "password"}

    _ph = argon2.PasswordHasher()

    @classmethod
    def create(cls, user_id: uuid.UUID, password: str):
        return cls(user_id=user_id, password=cls._ph.hash(password))

    def __init__(self, user_id: uuid.UUID, password: str):
        self.user_id = user_id
        self.password = password

    def verify(self, pure_password: str) -> bool:
        try:
            return self._ph.verify(self.password, pure_password)
        except argon2.exceptions.VerifyMismatchError:
            return False
