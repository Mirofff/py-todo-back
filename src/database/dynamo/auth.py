from types_aiobotocore_dynamodb import service_resource as aiodyno_types

from src.database.dynamo import common as dynamo_common
from src.models import auth as auth_models
from src.types import dynamo as dyno_types


def _token_key(token: auth_models.RefreshToken | auth_models.AccessToken) -> dyno_types.DynoItem:
    return {"pk": f"{token.jti}", "sk": token.type_}


async def put(dyno_table: aiodyno_types.Table, token: auth_models.RefreshToken | auth_models.AccessToken) -> None:
    await dynamo_common.put_item(dyno_table, token, _token_key(token))
