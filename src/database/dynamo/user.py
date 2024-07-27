import typing as t
import uuid

from types_aiobotocore_dynamodb import type_defs as aiodyno_defs

from src.database.dynamo import common as dynamo_common, connection as dynamo_connection
from src.exceptions import user as user_exceptions
from src.models import user as user_models


def _user_key(user_id: uuid.UUID) -> t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef]:
    return {"pk": f"{user_id}", "sk": "info"}


def _user_public_key(email: str) -> t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef]:
    return {"pk": email, "sk": "info"}


def _password_key(user_id: uuid.UUID) -> t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef]:
    return {"pk": f"{user_id}", "sk": "password"}


async def put(dyno: dynamo_connection.DynoConnection, user: user_models.User) -> None:
    await dynamo_common.put_item(dyno.main_table, user, _user_key(user.id_))

    await dynamo_common.put_item(dyno.main_table, user, _user_public_key(user.email))


async def get(dyno: dynamo_connection.DynoConnection, user_id: uuid.UUID) -> user_models.User:
    user = await dynamo_common.get_item(dyno.main_table, user_models.User, _user_key(user_id))
    if user:
        return user
    raise user_exceptions.UserNotFoundException(user_id)


async def get_by_email(dyno: dynamo_connection.DynoConnection, email: str) -> user_models.User | None:
    return await dynamo_common.get_item(dyno.main_table, user_models.User, _user_public_key(email))


async def new_password(dyno: dynamo_connection.DynoConnection, encrypted_password: user_models.UserPassword) -> None:
    await dynamo_common.put_item(dyno.main_table, encrypted_password, _password_key(encrypted_password.user_id))


async def get_password(dyno: dynamo_connection.DynoConnection, user_id: uuid.UUID) -> user_models.UserPassword:
    password = await dynamo_common.get_item(dyno.main_table, user_models.UserPassword, _password_key(user_id))
    if password:
        return password
    raise user_exceptions.UserPasswordNotFoundException(user_id)
