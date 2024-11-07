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
