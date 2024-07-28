"""
! TODO: Logging
"""

from src.database.dynamo import connection as dynamo_connection, user as user_dynamo
from src.exceptions import auth as auth_exceptions
from src.models import auth as auth_models, user as user_models


def generate_access_refresh(user: user_models.User) -> tuple[auth_models.AccessToken, auth_models.RefreshToken]:
    access_token, refresh_token = (
        auth_models.AccessToken.create(user.id_, user.email),
        auth_models.RefreshToken.create(user.id_),
    )

    return access_token, refresh_token


async def token_to_user(dyno: dynamo_connection.DynoConnection, access: auth_models.AccessToken) -> user_models.User:
    if not access.is_expired:
        return await user_dynamo.get(dyno, access.sub)
    raise auth_exceptions.AccessTokenExpired(access.exp)
