"""
! TODO: Logging
"""

import typing as t
import uuid

from boto3.dynamodb import conditions as boto_conditions

from src.database.dynamo import common as dynamo_common, connection as dynamo_connection
from src.exceptions import common as common_exceptions
from src.models import task as task_models, user as user_models
from src.types import dynamo as dyno_types


def _task_key(user: user_models.User, task_id: uuid.UUID = uuid.uuid4()) -> dyno_types.DynoItem:
    return {"pk": f"{user.id_}_tasks", "sk": f"{task_id}"}


def _tasks_where_user_is(user: user_models.User) -> boto_conditions.ConditionBase:
    return boto_conditions.Key("pk").eq(f"{user.id_}_tasks")


def _tasks_where_done_is(done_status: bool | None) -> boto_conditions.ConditionBase:
    condition = boto_conditions.Attr("is_done").exists()
    if done_status:
        condition &= boto_conditions.Attr("is_done").eq(int(done_status))
    return condition


def _tasks_where_tags_in(tags: t.Sequence[str] | None) -> boto_conditions.ConditionBase:
    condition = boto_conditions.Attr("is_done").exists()
    if tags:
        for tag in tags:
            condition &= boto_conditions.Attr("tags").contains(tag)
    return condition


async def get_task(
    dyno: dynamo_connection.DynoConnection, user: user_models.User, task_id: uuid.UUID
) -> task_models.Task:
    task = await dynamo_common.get_item(dyno.main_table, task_models.Task, key=_task_key(user, task_id))
    if task is None:
        raise common_exceptions.ModelItemNotFound[task_models.Task](task_id)
    return task


async def new_task(dyno: dynamo_connection.DynoConnection, user: user_models.User, task: task_models.Task):
    await dynamo_common.put_item(dyno.main_table, task, _task_key(user, task.id_))


async def update_task(
    dyno: dynamo_connection.DynoConnection, user: user_models.User, task_id: uuid.UUID, items: dict
) -> task_models.Task:
    return await dynamo_common.update_item(dyno.main_table, task_models.Task, items, _task_key(user, task_id))


async def filter(
    dyno: dynamo_connection.DynoConnection,
    user: user_models.User,
    page_info: dynamo_common.DataPageInfo,
    *,
    task_status: bool | None = None,
    where_tags: t.Sequence[str] | None = None,
) -> dynamo_common.DataPage[task_models.Task]:
    key = _tasks_where_user_is(user)
    filter = _tasks_where_done_is(done_status=task_status) & _tasks_where_tags_in(where_tags)

    return await dynamo_common.query_paginate(dyno, task_models.Task, key, page_info, filter)
