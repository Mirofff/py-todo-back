"""
! TODO: Logging
"""

from src.database.dynamo import connection as dynamo_connection
from src.database.dynamo import user as user_dynamo
from src.exceptions import user as user_exceptions
from src.models import user as user_models


async def register_new_user(
    dyno: dynamo_connection.DynoConnection, public_user: user_models.UserPublic, pure_password: str
) -> user_models.User:
    preexist_user = await user_dynamo.get_by_email(dyno, public_user.email)

    if preexist_user is None:
        user = user_models.User.create(public_user.email, public_user.first_name, public_user.last_name)
        encrypted_password = user_models.UserPassword.create(user.id_, pure_password)

        try:
            await user_dynamo.put(dyno, user)
            await user_dynamo.new_password(dyno, encrypted_password)

            return user

        except Exception:
            raise user_exceptions.UserException()

    raise user_exceptions.UserAlreadyExistException()


async def login_user(dyno: dynamo_connection.DynoConnection, email: str, pure_password: str) -> user_models.User | None:
    """try to find user by email and check password

    Args:
        dyno_table (aiodyno_types.Table)
        email (str)
        password (str)

    Returns:
        user_models.User | None

    Raises:
        user_exceptions.UserNotFoundException
    """
    public_user = await user_dynamo.get_by_email(dyno, email)

    if public_user:
        user = await user_dynamo.get(dyno, public_user.id_)
        user_password = await user_dynamo.get_password(dyno, public_user.id_)

        if user_password.verify(pure_password):
            return user

    return None
