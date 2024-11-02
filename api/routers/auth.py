from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form
from api.dependencies import scoped_session_db
from api.db import auth_qr
from jwt_auth import jwt_utils

router = APIRouter(
    prefix="/api/v1/jwt_auth",
    tags=["jwt_auth"],
)


@router.get("/register")
async def register_user(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    password_hash = jwt_utils.hash_password(password=password)
    result = await auth_qr.create_user(
        session=session,
        username=username,
        password_hash=password_hash
    )
    return {"result", result}


@router.post("/login")
async def login_user(username: str, password: str):
    return {"result", "OK"}
