from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    username: str


class UserInDB(UserSchema):
    password_hash: bytes


class TaskCreate(BaseModel):
    title: str = Field(max_length=50)
    description: str = Field(max_length=500)
    status: Literal["completed", "in_progress"] = "in_progress"


class TaskStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"


class Task(BaseModel):
    title: str
    description: str
    status: str


class TasksResponse(BaseModel):
    tasks: list[Task]
