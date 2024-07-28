"""
! TODO: Logging
"""

import typing as t
import uuid

import fastapi

from packages import common as common_package
from src.database.dynamo import common as dynamo_common
from src.entrypoints.rest.depends import auth as auth_depends, repositories as repositories_depends
from src.entrypoints.rest.dtos import common as common_dtos, tasks as tasks_dtos
from src.handlers import task as task_handlers
from src.models import task as task_models

router = fastapi.APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=common_dtos.DataPage)
async def get_user_tasks(
    user: auth_depends.AuthUserDepends,
    dyno: repositories_depends.DynoDepends,
    pagesize: int = fastapi.Query(100, gt=0, le=100),
    next_token: str | None = fastapi.Query(None),
    task_status: bool | None = fastapi.Query(None),
    tags: t.Sequence[str] | None = fastapi.Query(None),
):
    """
    Pagination endpoint for authenticated user

    ! TODO: enable encryption for starting token to prevent data select abuse
    """
    next_page = common_package.base64_to_dict(next_token)

    tasks = await task_handlers.filter(
        dyno, user, dynamo_common.DataPageInfo(pagesize, next_page), task_status=task_status, where_tags=tags
    )

    return common_dtos.DataPage[tasks_dtos.Task].model_validate(tasks)


@router.post("/", response_model=tasks_dtos.Task, status_code=fastapi.status.HTTP_201_CREATED)
async def create_task(
    user: auth_depends.AuthUserDepends, dyno: repositories_depends.DynoDepends, create_task_dto: tasks_dtos.TaskCreate
):
    """
    Create new task to authenticated user
    """
    task = task_models.Task.create(
        user, create_task_dto.title, create_task_dto.description, create_task_dto.tags, is_done=create_task_dto.is_done
    )

    await task_handlers.new_task(dyno, user, task)

    return tasks_dtos.Task.model_validate(task)


@router.patch("/{task_id}", response_model=tasks_dtos.Task, status_code=fastapi.status.HTTP_200_OK)
async def update_task(
    user: auth_depends.AuthUserDepends,
    dyno: repositories_depends.DynoDepends,
    task_id: uuid.UUID,
    update_task_dto: tasks_dtos.TaskUpdate,
):
    """
    Partial update for task.
    """
    task = await task_handlers.update_task(
        dyno, user, task_id, update_task_dto.model_dump(by_alias=False, exclude_none=True)
    )

    return tasks_dtos.Task.model_validate(task)
