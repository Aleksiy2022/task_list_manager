from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes


class Task(BaseModel):
    title: str = Field(max_length=50)
    description: str = Field(max_length=500)
    status: Literal["completed", "in_progress"] = "in_progress"
