from typing import Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.dbhelper import db_helper
from jwt.exceptions import InvalidTokenError
from jwt_auth import jwt_utils
from fastapi import Form, HTTPException, status, Depends
from api.db import user_qr
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/",
)


async def scoped_session_db() -> AsyncGenerator[AsyncSession, None]:
    session = db_helper.get_scoped_session()
    try:
        yield session
    finally:
        await session.close()


async def validate_auth_user(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        session: Annotated[AsyncSession, Depends(scoped_session_db)]
):
    unauthed_exp = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    user = await user_qr.get_user_by_username(
        session=session,
        username=username
    )
    if not user:
        raise unauthed_exp
    if await jwt_utils.validate_password(
            password=password,
            hashed_password=user.password_hash
    ):
        return user

    raise unauthed_exp


async def get_current_token_payload(
        token: Annotated[str, Depends(oauth2_scheme)]
):
    try:
        payload = await jwt_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_auth_user(
        payload: Annotated[dict, Depends(get_current_token_payload)],
        session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    username: str = payload.get("username")
    user = await user_qr.get_user_by_username(
        session=session,
        username=username
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user
