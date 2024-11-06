from typing import Annotated

from fastapi import APIRouter, Form, Depends
from api.dependencies import get_current_auth_user
from api.core import schemas

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["tasks"],
)


@router.post("/")
async def create_task(
        task: Annotated[schemas.Task, Form()],
        user: Annotated[schemas.UserSchema, Depends(get_current_auth_user)],
):
    return {"result": task}
