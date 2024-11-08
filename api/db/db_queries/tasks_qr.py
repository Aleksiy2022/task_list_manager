from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.models import Task
from api.core import schemas
from sqlalchemy import select


async def create_task(
        session: AsyncSession,
        user_id: int,
        task_data: schemas.TaskCreate,
) -> bool:
    """
    Create a new task in the database.

    Parameters
    ----------
    session : AsyncSession
        An active SQLAlchemy asynchronous session used for database
        operations.
    user_id : int
        The ID of the user to whom the task is assigned.
    task_data : TaskCreate
        An instance containing the data required to create a new task.
        Must include `title`, `description`, and `status`.

    Returns
    -------
    bool
        Returns `True` if the task was successfully created and
        committed to the database.
    """
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        user_id=user_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return True


async def get_tasks(
        session: AsyncSession,
        status: str,
) -> list[schemas.Task]:
    """
    Retrieve a list of tasks from the database based on their status.

    Parameters
    ----------
    session : AsyncSession
        An active SQLAlchemy asynchronous session used for database operations.
    status : str
        The status of the tasks to be retrieved (e.g., "pending", "completed").

    Returns
    -------
    list[Task]
        A list of task instances that match the specified status.
        If no tasks match the status, an empty list will be returned.
    """
    stmt = select(Task).where(Task.status == status)
    tasks = await session.scalars(stmt)

    return list(tasks)


async def update_task(
        session: AsyncSession,
        task_id: int,
        update_data: schemas.TaskUpdate
):
    """
    Update a task in the database with the provided
    task ID and update data.

    Parameters
    ----------
    session : AsyncSession
        An active SQLAlchemy asynchronous session used
        for database operations.
    task_id : int
        The unique identifier of the task to be updated.
    update_data : schemas.TaskUpdate
        An instance containing the fields to update. It may include:
        - title (str, optional): The new title for the task.
        - description (str, optional): The new description for the task.
        - status (str, optional): The new status for the task.

    Returns
    -------
    Task
        The updated task instance after applying the changes.
    """
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalars().one_or_none()

    if task is None:
        raise NoResultFound(f"Task with id {task_id} not found.")

    if update_data.title is not None:
        task.title = update_data.title
    if update_data.description is not None:
        task.description = update_data.description
    if update_data.status is not None:
        task.status = update_data.status

    session.add(task)

    await session.commit()
    return task


async def delete_task(
        session: AsyncSession,
        task_id: int,
) -> bool:
    """
    Delete a task from the database with the specified task ID.

    Parameters
    ----------
    session : AsyncSession
        An active SQLAlchemy asynchronous session used for database operations.

    task_id : int
        The unique identifier of the task to be deleted.

    Returns
    -------
    bool
        True if the task was successfully deleted, False if no task with
        the specified task_id exists.
    """
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task_to_delete = result.scalars().one_or_none()
    if task_to_delete is None:
        return False
    await session.delete(task_to_delete)
    await session.commit()
    return True
