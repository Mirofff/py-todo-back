import contextlib
import typing as t

import aioboto3
import pydantic
import types_aiobotocore_dynamodb as aiodyno_types
from boto3.dynamodb import conditions as dynamo_conditions, types as dynamo_types
from botocore import exceptions as boto_exceptions
from types_aiobotocore_dynamodb import service_resource as aiodyno_service_types, type_defs as aiodyno_defs


class DynoConnection:
    _table_connections: t.MutableMapping[str, aiodyno_service_types.Table] = {}

    _builder = dynamo_conditions.ConditionExpressionBuilder()
    serializer = dynamo_types.TypeSerializer()
    deserializer = dynamo_types.TypeDeserializer()

    def __init__(self, db_endpoint: pydantic.HttpUrl, access_key: str, secret_key: str):
        self.db_endpoint = db_endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self._dyno_main_table: aiodyno_service_types.Table
        self._dyno_tokens_table: aiodyno_service_types.Table
        self._main_table_name: str
        self._tokens_table_name: str

    async def __aenter__(self) -> t.Self:
        session = aioboto3.Session()

        self.context_stack = contextlib.AsyncExitStack()

        self._dyno_resource: aiodyno_service_types.DynamoDBServiceResource = (
            await self.context_stack.enter_async_context(
                session.resource(  # type: ignore
                    service_name="dynamodb",
                    region_name="us-west-1",
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    endpoint_url=str(self.db_endpoint),
                )
            )
        )
        self._dyno_client = await self.context_stack.enter_async_context(
            session.client(
                service_name="dynamodb",
                region_name="us-west-1",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=str(self.db_endpoint),
            )
        )

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.context_stack.aclose()

    @property
    def dyno_resource(self) -> aiodyno_service_types.DynamoDBServiceResource:
        return self._dyno_resource

    @property
    def dyno_client(self) -> aiodyno_types.DynamoDBClient:
        return self._dyno_client

    async def register_main_table(self, table_name: str) -> None:
        self._main_table_name = table_name
        self._dyno_main_table = await self._register_table(table_name)

    async def register_tokens_table(self, table_name: str) -> None:
        self._tokens_table_name = table_name
        self._dyno_tokens_table = await self._register_table(table_name)

    @property
    def main_table(self) -> aiodyno_service_types.Table:
        return self._dyno_main_table

    def main_table_paginate(
        self,
        key_condition: dynamo_conditions.ConditionBase,
        pagesize: int | None = None,
        max_items: int | None = None,
        starting_token: str | None = None,
    ) -> t.AsyncIterator[aiodyno_defs.QueryOutputTypeDef]:
        expr = self._builder.build_expression(key_condition, is_key_condition=True)

        pagination_config: aiodyno_defs.PaginatorConfigTypeDef = {}
        if pagesize:
            pagination_config.update({"PageSize": pagesize})
        if max_items:
            pagination_config.update({"MaxItems": max_items})
        if starting_token:
            pagination_config.update({"StartingToken": starting_token})

        return self._dyno_client.get_paginator("query").paginate(
            TableName=self._main_table_name,
            KeyConditionExpression=expr.condition_expression,
            ExpressionAttributeValues={
                k: self.serializer.serialize(v) for k, v in expr.attribute_value_placeholders.items()
            },
            ExpressionAttributeNames=expr.attribute_name_placeholders,
            PaginationConfig=pagination_config,
        )

    @property
    def tokens_table(self) -> aiodyno_service_types.Table:
        return self._dyno_tokens_table

    @property
    def tokens_table_paginator(self): ...

    async def _register_table(self, table_name: str) -> aiodyno_service_types.Table:
        preexist_dyno_table = self._table_connections.get(table_name)
        if preexist_dyno_table is None:
            try:
                await self._dyno_client.describe_table(TableName=table_name)

            except boto_exceptions.ClientError:
                # assert e.response["Error"]["Code"] == "ResourceNotFoundException"
                await self._create_table(table_name)

            finally:
                dyno_table = await self._dyno_resource.Table(table_name)
                self._table_connections[table_name] = dyno_table
                return dyno_table
        return preexist_dyno_table

    async def _create_table(self, table_name: str, pk_name: str = "pk", sk_name: str = "sk") -> None:
        await self._dyno_client.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {"AttributeName": pk_name, "AttributeType": "S"},
                {"AttributeName": sk_name, "AttributeType": "S"},
            ],
            KeySchema=[{"AttributeName": pk_name, "KeyType": "HASH"}, {"AttributeName": sk_name, "KeyType": "RANGE"}],
            BillingMode="PAY_PER_REQUEST",
        )
        await self._dyno_client.get_waiter("table_exists").wait(TableName=table_name)
