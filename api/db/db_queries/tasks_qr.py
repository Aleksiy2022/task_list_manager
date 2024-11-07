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
    stmt = select(Task).where(Task.status == status)
    tasks = await session.scalars(stmt)

    return list(tasks)


async def update_task(
        session: AsyncSession,
        task_id: int,
        update_data: schemas.TaskUpdate
):
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
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task_to_delete = result.scalars().one_or_none()
    if task_to_delete is None:
        return False
    await session.delete(task_to_delete)
    await session.commit()
    return True
