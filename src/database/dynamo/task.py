import typing as t
import uuid

from types_aiobotocore_dynamodb import service_resource as aiodyno_types
from types_aiobotocore_dynamodb import type_defs as aiodyno_defs

from src.database.dynamo import common as dynamo_common
from src.models import task as task_models
from src.models import user as user_models


def _key(task_id: uuid.UUID, user_id: uuid.UUID) -> t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef]:
    return {"pk": f"user_{user_id}", "sk": f"{task_id}"}


async def new(dyno_table: aiodyno_types.Table, user: user_models.User, task: task_models.Task) -> None:
    await dynamo_common.put_item(dyno_table, task, _key(task.id_, user.id_))
