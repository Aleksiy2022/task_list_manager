from typing import Annotated, AsyncGenerator

from aioredis import Redis
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

import api.routers.auth.auth
import api.routers.auth.auth_helpers
from api.core import schemas, settings
from api.db import user_qr
from api.db.dbhelper import db_helper
from api.redis_client import redis
from api.routers.auth import jwt_utils

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/",
)


async def scoped_session_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a new session for each request and ensures it is closed after use.

    Yields
    ------
    AsyncSession
        An asynchronous session object for database operations.
    """
    session = db_helper.get_scoped_session()
    try:
        yield session
    finally:
        await session.close()


async def get_redis() -> Redis:
    """
    Get a Redis connection instance

    Returns
    -------
        Redis
    """
    return redis


async def validate_auth_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(scoped_session_db)],
):
    """
    Validate user authentication credentials.

    Parameters
    ----------
    username : str
        The username of the user attempting to authenticate.
    password : str
        The password of the user attempting to authenticate.
    session : AsyncSession
        An asynchronous session instance for database interaction.

    Returns
    -------
    User
        If authentication is successful, returns the user object
        corresponding to the provided username.

    Raises
    ------
    HTTPException
        Raises an HTTP 401 Unauthorized exception if the username
        does not exist or the password is incorrect.

    """
    unauthed_exp = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    user = await user_qr.get_user_by_username(session=session, username=username)
    if not user:
        raise unauthed_exp
    if await api.routers.auth.auth_helpers.validate_password(
        password=password, hashed_password=user.password_hash
    ):
        return user

    raise unauthed_exp


async def get_current_token_payload(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Extract and validate the payload from a JWT token.

    Parameters
    ----------
    token : str
        The JWT token to decode.

    Returns
    -------
    dict
        The decoded payload of the JWT token
    Raises
    ------
    HTTPException
        Raises an HTTP 401 Unauthorized exception if the token is
        invalid or cannot be decoded.
    """
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
    """
    Validate the type of given token against an expected token type.

    Parameters
    ----------
    payload : dict
        A dictionary containing the decoded JWT token payload
    token_type : str
        The expected token type that the payload should contain.

    Returns
    -------
    bool
        Returns True if the token type in the payload matches the
        expected token type.

    Raises
    ------
    HTTPException
        Raises an HTTP 401 Unauthorized exception if the token type
        in the payload does not match the expected type.
    """
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
    """
    Retrieve a user from the database based on the 'sub' claim
    in the token payload.

    Parameters
    ----------
    payload : dict
        A dictionary containing the decoded JWT token payload
    session : AsyncSession
        An instance of AsyncSession for database operations.

    Returns
    -------
    UserSchema
        An instance of `UserSchema` representing the
        user associated with the provided user ID (from 'sub' claim).

    Raises
    ------
    HTTPException
        Raises an HTTP 401 Unauthorized exception if no user is found
        with the provided user ID, indicating that the token is invalid.
    """
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
    """
    A class to retrieve user information from a token payload.

    This class is designed to validate the token type and obtain
    the user associated with that token.

    Parameters
    ----------
    token_type : str
        The expected type of the token (e.g., 'access', 'refresh').
    """

    def __init__(self, token_type: str):
        """
        Initializes the UserGetterFromToken with a specified token type.

        Parameters
        ----------
        token_type : str
            The expected token type to validate against during the call.
        """
        self.token_type = token_type

    async def __call__(
        self,
        payload: dict = Depends(get_current_token_payload),
        session: AsyncSession = Depends(scoped_session_db),
    ) -> schemas.UserSchema:
        """
        Validates the token type and retrieves the user associated
        with the provided token payload. This method first checks if
        the token type of the provided payload matches the expected token
        type. If valid, it then retrieves the user information.

        Parameters
        ----------
        payload : dict
            A dictionary containing the decoded JWT token payload
        session : AsyncSession
            An instance of AsyncSession for database operations.

        Returns
        -------
        UserSchema
            An instance of `schemas.UserSchema` representing
            the user associated with the provided token payload.

        """
        await validate_token_type(payload, self.token_type)
        return await get_user_by_token_sub(payload=payload, session=session)


get_current_auth_user = UserGetterFromToken(settings.auth_jwt.ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UserGetterFromToken(
    settings.auth_jwt.REFRESH_TOKEN_TYPE
)
