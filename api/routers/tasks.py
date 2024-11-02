from typing import Annotated

from fastapi import APIRouter, Query

from ..db import Task

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["tasks"],
)


@router.post("/")
async def create_task(task: Annotated[Task, Query()]):
    return {"result": task}
