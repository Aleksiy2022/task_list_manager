from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form
from api.dependencies import scoped_session_db, validate_auth_user
from api.db import user_qr
from api.core import schemas
from jwt_auth import jwt_utils
from .auth_helpers import create_access_token, create_refresh_token


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.post("/register")
async def register_user(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    password_hash = await jwt_utils.hash_password(password=password)
    if not await user_qr.create_user(
            session=session,
            username=username,
            password_hash=password_hash
    ):
        return {"Invalid data"}
    else:
        return {f"Hello, {username.capitalize()}!"}


@router.post("/login", response_model=schemas.TokenInfo)
async def login_user(
        user: schemas.UserSchema = Depends(validate_auth_user),
):
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)
    return schemas.TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=schemas.TokenInfo,
    response_model_exclude_none=True,
)
async def refresh_jwt(
    user: schemas.UserSchema = Depends(validate_auth_user),
):
    access_token = await create_access_token(user)
    return schemas.TokenInfo(
        access_token=access_token,
    )
