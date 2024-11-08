from typing import Annotated

from fastapi import (
    APIRouter,
    Form,
    Depends,
    Response,
    status,
    Query, HTTPException,
)
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
    """
    Create a new task associated with the current authenticated user.

    Parameters
    ----------
    task : TaskCreate.
        An instance of TaskCreate schema containing the details of the task
    to be created.
    user : UserSchema.
        An instance of UserSchema representing the currently authenticated user.
    session : AsyncSession.
        An instance of AsyncSession for database operations.

    Returns
    -------
    Response :
        An HTTP response with status code 200 if the task creation is
        successful, or status code 422 UNPROCESSABLE ENTITY if the
        task creation fails.
    """
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
    """
    Retrieve all tasks filtered by a specified task status.

    Parameters
    ----------
    status_filter : TaskStatus.
        The status filter used to retrieve specific tasks.
    user : UserSchema.
        An instance of UserSchema representing the currently authenticated user.
    session : AsyncSession.
        An instance of AsyncSession for database operations.

    Returns
    -------
    TasksResponse :
        A structured response containing a list of tasks.
    """
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
    """

    Parameters
    ----------
    id : int.
        The unique identifier of the task to be updated.
    task : TaskUpdate.
        An instance of TaskUpdate schema containing the fields that are
        to be updated for the specified task.
    user : UserSchema.
        An instance of UserSchema representing the currently authenticated user.
    session : AsyncSession.
        An instance of AsyncSession for database operations.

    Returns
    -------
    Task :
        The updated task object that reflects the changes made.
    """
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
    """

    Parameters
    ----------
    id : int.
        The unique identifier of the task to be deleted.
    user : UserSchema.
        An instance of UserSchema representing the currently authenticated user.
    session : AsyncSession.
        An instance of AsyncSession for database operations.

    Returns
    -------
    dict:
        A dictionary containing a success message confirming the deletion
        of the specified task.
    """
    result = await tasks_qr.delete_task(
            session=session,
            task_id=id,
        )
    if not result:
        raise HTTPException(status_code=404, detail=f"Task with id: {id} not found.")
    return {"message": f"Task with id: {id} successfully deleted"}
