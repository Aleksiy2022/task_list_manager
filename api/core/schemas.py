import re
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    username: str


class UserCreate(BaseModel):
    username: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=16)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(
        cls,
        password: str,
    ):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError(
                "The password must contain at least one special character."
            )

        if not re.search(r"[A-Z]", password):
            raise ValueError("The password must contain at least one capital letter.")

        if not re.search(r"[a-z]", password):
            raise ValueError("The password must contain at least one lowercase letter.")
        return password


class TaskCreate(BaseModel):
    title: str = Field(max_length=50)
    description: str = Field(max_length=500)
    status: Literal["completed", "in_progress"] = "in_progress"


class TaskUpdate(BaseModel):
    title: str | None = Field(max_length=50)
    description: str | None = Field(max_length=500)
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
