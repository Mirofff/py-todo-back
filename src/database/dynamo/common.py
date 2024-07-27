"""
TODO: DynamoDB response processing (logging consumed WCU, RCU, etc.)
"""

import typing as t

from boto3.dynamodb import conditions as boto_conditions
from types_aiobotocore_dynamodb import service_resource as aiodyno_service_types, type_defs as aiodyno_defs

from src.database.dynamo import connection as dyno_connection, serializers as dyno_serializers, common as dynamo_common
from src.types import abstract as abstract_types, dynamo as dynamo_types

_T = t.TypeVar("_T", bound=abstract_types.AbstractDomainModel)


class DataPageInfo:
    def __init__(self, pagesize: int, next_page: t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef] | None):
        self.pagesize = pagesize
        self.next_page = next_page


class DataPage(t.Generic[_T]):
    def __init__(
        self,
        items: t.Sequence[_T],
        pagesize: int,
        next_page: t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef] | None,
    ) -> None:
        self.items = items
        self.info = DataPageInfo(pagesize, next_page)


async def get_item(dyno_table: aiodyno_service_types.Table, model: t.Type[_T], key: dynamo_types.DynoItem) -> _T | None:
    resp = await dyno_table.get_item(Key=key)
    item = resp.get("Item")
    if item is not None:
        return model(**dyno_serializers.dynamo_item_to_python(item))
    return None


async def query_paginate(
    dyno: dyno_connection.DynoConnection,
    model: t.Type[_T],
    keys_condition: boto_conditions.ConditionBase,
    page_info: dynamo_common.DataPageInfo,
    attr_condition: boto_conditions.ConditionBase,
) -> DataPage:
    params = {"KeyConditionExpression": keys_condition, "Limit": page_info.pagesize, "FilterExpression": attr_condition}

    if page_info.next_page:
        params["ExclusiveStartKey"] = page_info.next_page

    resp = await dyno.main_table.query(**params)

    return DataPage(
        [model(**dyno_serializers.dynamo_item_to_python(item)) for item in resp["Items"]],
        resp["Count"],
        resp.get("LastEvaluatedKey"),
    )


async def put_item(
    dyno_table: aiodyno_service_types.Table, model_item: abstract_types.AbstractDomainModel, key: dynamo_types.DynoItem
) -> None:
    item = model_item.to_dict()
    item.update(key)
    item = dyno_serializers.serialize(item)

    await dyno_table.put_item(Item=item)


async def delete_item(dyno_table: aiodyno_service_types.Table, key: dynamo_types.DynoItem) -> None:
    await dyno_table.delete_item(Key=key)


async def update_item(
    dyno_table: aiodyno_service_types.Table, model: t.Type[_T], update_data: t.Mapping, key: dynamo_types.DynoItem
) -> _T:
    dynamo_user = dyno_serializers.serialize(update_data)
    update_expression = "SET "
    expression_attribute_names = {}
    expression_attribute_values = {}
    for _key, _value in dynamo_user.items():
        update_expression += f"#attr_{_key} = :val_{_key},"
        expression_attribute_names[f"#attr_{_key}"] = _key
        expression_attribute_values[f":val_{_key}"] = _value

    update_expression = update_expression[:-1]

    resp = await dyno_table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="ALL_NEW",
        ReturnConsumedCapacity="TOTAL",
        ReturnItemCollectionMetrics="SIZE",
    )

    return model(**dyno_serializers.dynamo_item_to_python(resp["Attributes"]))
