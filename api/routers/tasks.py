from typing import Annotated

from fastapi import (
    APIRouter,
    Form,
    Depends,
    Response,
    status,
    Query, HTTPException,
)
from sqlalchemy.exc import NoResultFound
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


@router.put("/id", response_model=schemas.Task)
async def update_task(
        id: Annotated[int, Query()],
        task: Annotated[schemas.TaskUpdate, Form()],
        user: Annotated[schemas.UserSchema, Depends(get_current_auth_user)],
        session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    updated_task = await tasks_qr.update_task(
        task_id=id,
        update_data=task,
        session=session
    )
    return updated_task


@router.delete("/id")
async def delete_task(
        id: Annotated[int, Query()],
        user: Annotated[schemas.UserSchema, Depends(get_current_auth_user)],
        session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    result = await tasks_qr.delete_task(
            session=session,
            task_id=id,
        )
    if not result:
        raise HTTPException(status_code=404, detail=f"Task with id: {id} not found.")
    return {"message": f"Task with id: {id} successfully deleted"}
