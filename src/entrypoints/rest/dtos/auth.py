import datetime
import enum
import typing as t

import fastapi

from ._base import FromAttributesBaseModel


class GrantType(enum.StrEnum):
    password = "password"
    # authorization_code = "authorization_code"  # TODO: need to add client id and client secret support
    # client_credentials = "client_credentials"


class TokenType(enum.StrEnum):
    bearer = "Bearer"


class AuthCredentials(FromAttributesBaseModel):
    grant_type: GrantType
    username: str
    password: str
    scope: str | None
    client_id: str | None
    client_secret: str | None

    @classmethod
    def as_form(
        cls,
        grant_type: t.Annotated[GrantType, fastapi.Form()],
        username: t.Annotated[str, fastapi.Form()],
        password: t.Annotated[str, fastapi.Form()],
        scope: t.Annotated[str, fastapi.Form()] = "",
        client_id: t.Annotated[str | None, fastapi.Form()] = "",
        client_secret: t.Annotated[str | None, fastapi.Form()] = "",
    ):
        return cls(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )


class AuthSuccess(FromAttributesBaseModel):
    access_token: str
    refresh_token: str
    expires_in: datetime.datetime
    scope: None = None


AuthCredentialsFormDepends = t.Annotated[AuthCredentials, fastapi.Depends(AuthCredentials.as_form)]
