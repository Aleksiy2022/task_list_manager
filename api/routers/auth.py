from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
)
from api.dependencies import (
    scoped_session_db,
    validate_auth_user,
    get_current_auth_user_for_refresh,
    get_redis,
)
from datetime import timedelta
from aioredis import Redis
from api.db import user_qr
from api.core import schemas, settings
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
        redis: Annotated[Redis, Depends(get_redis)],
        user: schemas.UserSchema = Depends(validate_auth_user),
):
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)

    await redis.set(
        f"refresh_token_{user.id}",
        refresh_token,
        ex=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )
    saved_token = await redis.get(f"refresh_token_{user.id}")
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
        redis: Annotated[Redis, Depends(get_redis)],
        user: Annotated[schemas.UserSchema, Depends(get_current_auth_user_for_refresh)],
):
    stored_refresh_token = await redis.get(f"refresh_token_{user.id}")
    if stored_refresh_token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = await create_access_token(user)
    return schemas.TokenInfo(
        access_token=access_token,
    )
