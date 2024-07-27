import datetime
import decimal
import typing as t
import uuid

from boto3.dynamodb import types as dyno_types
from types_aiobotocore_dynamodb import type_defs as aiodyno_defs

_deserializer = dyno_types.TypeDeserializer()
_serializer = dyno_types.TypeSerializer()


def _serialize(value: t.Any) -> t.Any:
    # if isinstance(value, dict):
    #     return serialize(value)
    if isinstance(value, int) or isinstance(value, float):
        return decimal.Decimal(value)
    if isinstance(value, datetime.datetime):
        return decimal.Decimal(value.timestamp())
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def serialize(source: t.Mapping) -> t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef]:
    serialized = {}

    for key, value in source.items():
        serialized_key = str(key)

        if isinstance(value, dict):
            serialized[serialized_key] = serialize(value)
        else:
            serialized[serialized_key] = _serialize(value)

    return serialized


def dynamo_item_to_python(dynamo_object: dict) -> dict:
    return {k: v for k, v in dynamo_object.items() if k not in ("pk", "sk")}
