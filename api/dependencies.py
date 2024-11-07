from typing import Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.dbhelper import db_helper
from api.core import settings, schemas
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


async def validate_token_type(
        payload: dict,
        token_type: str,
) -> bool:
    current_token_type_field = payload.get(settings.auth_jwt.TOKEN_TIPE_FIELD)
    if current_token_type_field == token_type:

        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token type {current_token_type_field!r} expected {token_type!r}.",
    )


async def get_user_by_token_sub(
        payload: dict,
        session: AsyncSession,
) -> schemas.UserSchema:
    user_id: int = payload.get("sub")
    user = await user_qr.get_user_by_id(
        session=session,
        id=user_id,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user


class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        payload: dict = Depends(get_current_token_payload),
        session: AsyncSession = Depends(scoped_session_db),
    ):
        await validate_token_type(payload, self.token_type)
        return await get_user_by_token_sub(
            payload=payload,
            session=session
        )


get_current_auth_user = UserGetterFromToken(settings.auth_jwt.ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UserGetterFromToken(settings.auth_jwt.REFRESH_TOKEN_TYPE)
