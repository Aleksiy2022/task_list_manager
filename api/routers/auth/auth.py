from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
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
from api.routers.auth.auth_helpers import create_access_token, create_refresh_token, hash_password

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.post("/register")
async def register_user(
        user: Annotated[schemas.UserCreate, Form()],
        session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    """
    Register a new user.

    This asynchronous endpoint allows the registration of a new user
    by accepting the necessary user information and validating the input data.

    Parameters
    ----------
    user : UserCreate.
        The user data provided in the request form, which includes fields for
        username and password.
    session : AsyncSession.
        An instance of AsyncSession for database operations.

    Returns
    -------
    dict :
        A dictionary containing a success message if
        the registration is successful.
    """
    password_hash = await hash_password(password=user.password)
    try:
        await user_qr.create_user(
                session=session,
                username=user.username,
                password_hash=password_hash
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"User with username: {user.username} already exists. "
                f"Try another one username."
            )
        )
    else:
        return {f"Hello, {user.username.capitalize()}!"}


@router.post("/login", response_model=schemas.TokenInfo)
async def login_user(
        redis: Annotated[Redis, Depends(get_redis)],
        user: schemas.UserSchema = Depends(validate_auth_user),
):
    """
    Log in a user and create access and refresh tokens.

    Parameters
    ----------
    redis : Redis.
        An instance of Redis used for storing the refresh token
        associated with the user.
    user : UserSchema.
        The user data that has been validated for authentication.

    Returns
    -------
    TokenInfo :
        An instance of TokenInfo containing both the access token and
        refresh token generated for the user.
    """
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)

    await redis.set(
        f"refresh_token_{user.id}",
        refresh_token,
        ex=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )
    await redis.get(f"refresh_token_{user.id}")
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
    """
    Refresh the JSON Web Token (JWT) for an authenticated user.

    Parameters
    ----------
    redis : Redis.
        An instance of Redis used for storing the refresh token
        associated with the user.
    user : UserSchema.
        The user data that has been validated for authentication.
        This is obtained through the `validate_auth_user` dependency.

    Returns
    -------
    TokenInfo.
        An instance of TokenInfo containing the newly generated access token
        for the user.
    """
    stored_refresh_token = await redis.get(f"refresh_token_{user.id}")
    if stored_refresh_token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = await create_access_token(user)
    return schemas.TokenInfo(
        access_token=access_token,
    )
