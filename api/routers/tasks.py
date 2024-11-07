from typing import Annotated

from fastapi import APIRouter, Form, Depends, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import (
    get_current_auth_user,
    scoped_session_db,
)
from api.core import schemas
from api.db import tasks_qr

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["tasks"],
)


@router.post("/")
async def create_task(
        task: Annotated[schemas.TaskCreate, Form()],
        user: Annotated[schemas.UserSchema, Depends(get_current_auth_user)],
        session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    result = await tasks_qr.create_task(
        session=session,
        user_id=user.id,
        task_data=task,
    )
    if result:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@router.get("/", response_model=schemas.TasksResponse)
async def get_tasks(
    status_filter: schemas.TaskStatus,
    user: Annotated[schemas.UserSchema, Depends(get_current_auth_user)],
    session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    tasks = await tasks_qr.get_tasks(
        session=session,
        status=status_filter,
    )
    task_response = [
        {
            "title": task.title,
            "description": task.description,
            "status": task.status
        }
        for task in tasks
    ]
    return {
        "tasks": task_response
    }
