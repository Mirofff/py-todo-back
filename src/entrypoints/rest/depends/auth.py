"""
! TODO: Logging
"""

import typing as t

import fastapi
import jwt
from fastapi import security as fastapi_security

from src.entrypoints.rest.depends import repositories as repositories_depends
from src.exceptions import auth as auth_exceptions
from src.handlers import auth as auth_handlers
from src.models import auth as auth_models, user as user_models

OAuthDepend = t.Annotated[
    str | None, fastapi.Depends(fastapi_security.OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False))
]
BearerDepend = t.Annotated[
    str | None, fastapi.Depends(fastapi_security.APIKeyHeader(name="Authorization", auto_error=False))
]


def _multi_auth_depend(oauth: OAuthDepend, bearer: BearerDepend):
    print("ha")
    if oauth:
        return oauth
    elif bearer:
        return bearer
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _get_current_user(
    dyno: repositories_depends.DynoDepends, token: str = fastapi.Depends(_multi_auth_depend)
) -> user_models.User:
    try:
        access = auth_models.AccessToken.from_jwt(token)
        user = await auth_handlers.token_to_user(dyno, access)

        return user

    except jwt.InvalidTokenError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth_exceptions.AccessTokenExpired as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail=f"Access token is expired! Expired at {e.expired_at}",
            headers={"WWW-Authenticate": "Bearer"},
        )


AuthUserDepends = t.Annotated[user_models.User, fastapi.Depends(_get_current_user)]
