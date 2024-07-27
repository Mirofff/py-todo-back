import datetime
import typing as t
import uuid

import jwt

from settings import config
from src.types import abstract as abstract_types

issuer = "https://todoapp.com"


class AccessToken(abstract_types.AbstractDomainModel):
    __slots__ = {"jti", "iss", "sub", "iat", "exp", "email", "current_datetime"}
    type_ = "access"

    def __init__(
        self,
        jti: uuid.UUID,
        iss: str,
        sub: uuid.UUID,
        iat: datetime.datetime,
        exp: datetime.datetime,
        email: str,
        current_datetime: datetime.datetime,
    ):
        self.current_datetime = current_datetime
        self.jti = jti
        self.iss = iss
        self.sub = sub
        self.iat = iat
        self.exp = exp
        self.email = email

    @classmethod
    def create(cls, sub: uuid.UUID, email: str, *, iss: str = issuer):
        # self.aud: str = TODO: need to add client id and client secret to implementation
        obj = cls.__new__(cls)

        current_datetime = datetime.datetime.now()

        obj.current_datetime = current_datetime
        obj.jti = uuid.uuid4()
        obj.iss = iss
        obj.sub = sub
        obj.iat = current_datetime
        obj.exp = current_datetime + datetime.timedelta(minutes=config.ACCESS_TOKEN_EXPIRATION)
        obj.email = email

        return obj

    @property
    def jwt(self) -> str:
        return jwt.encode(
            {
                "jti": str(self.jti),
                "iss": self.iss,
                "sub": str(self.sub),
                "exp": int(self.exp.timestamp()),
                "iat": int(self.iat.timestamp()),
                "email": self.email,
                "type": self.type_,
            },
            config.SIGNING_KEY,
            "HS256",
        )

    @classmethod
    def from_jwt(cls, token: str) -> t.Self:
        dict_token = jwt.decode(token, config.SIGNING_KEY, ["HS256"])

        return cls(
            jti=uuid.UUID(dict_token["jti"]),
            iss=dict_token["iss"],
            sub=uuid.UUID(dict_token["sub"]),
            iat=datetime.datetime.fromtimestamp(dict_token["iat"]),
            exp=datetime.datetime.fromtimestamp(dict_token["exp"]),
            email=dict_token["email"],
            current_datetime=datetime.datetime.fromtimestamp(dict_token["iat"]),
        )

    @property
    def is_expired(self) -> bool:
        if self.exp < datetime.datetime.now():
            return True
        return False


class RefreshToken(abstract_types.AbstractDomainModel):
    __slots__ = {"jti", "iss", "sub", "iat", "exp", "current_datetime"}
    type_: str = "refresh"

    def __init__(
        self,
        jti: uuid.UUID,
        iss: str,
        sub: uuid.UUID,
        iat: datetime.datetime,
        exp: datetime.datetime,
        current_datetime: datetime.datetime,
    ):
        self.jti = jti
        self.iss = iss
        self.sub = sub
        self.iat = iat
        self.exp = exp
        self.current_datetime = current_datetime

    @classmethod
    def create(cls, sub: uuid.UUID, *, iss: str = issuer):
        obj = cls.__new__(cls)

        obj.current_datetime = datetime.datetime.now()

        obj.jti = uuid.uuid4()
        obj.iss = iss
        obj.sub = sub
        # self.aud: str = TODO: need to add client id and client secret to implementation
        obj.iat = obj.current_datetime
        obj.exp = obj.current_datetime + datetime.timedelta(minutes=config.ACCESS_TOKEN_EXPIRATION)

        return obj

    @property
    def jwt(self) -> str:
        return jwt.encode(
            {
                "jti": str(self.jti),
                "iss": self.iss,
                "sub": str(self.sub),
                "exp": int(self.exp.timestamp()),
                "iat": int(self.iat.timestamp()),
                "type": self.type_,
            },
            config.SIGNING_KEY,
            "HS256",
        )

    @classmethod
    def from_jwt(cls, token: str) -> t.Self:
        dict_token = jwt.decode(token, config.SIGNING_KEY, ["HS256"])
        return cls(
            jti=uuid.UUID(dict_token["jti"]),
            iss=dict_token["iss"],
            sub=uuid.UUID(dict_token["sub"]),
            exp=datetime.datetime.fromtimestamp(dict_token["exp"]),
            iat=datetime.datetime.fromtimestamp(dict_token["iat"]),
            current_datetime=datetime.datetime.fromtimestamp(dict_token["iat"]),
        )
