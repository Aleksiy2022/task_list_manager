from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from api.dependencies import scoped_session_db
from api.db import auth_qr

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.get("/register")
async def register_user(
        username: str,
        password: str,
        session: Annotated[AsyncSession, Depends(scoped_session_db)]
):
    result = await auth_qr.create_user(
        session=session,
        username=username,
        password_hash=password
    )
    return {"result", result}


@router.post("/login")
async def login_user(username: str, password: str):
    return {"result", "OK"}
