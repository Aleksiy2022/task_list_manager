from datetime import timedelta

import bcrypt

from api.core import schemas
from api.core.config import settings
from api.routers.auth.jwt_utils import encode_jwt


async def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    """
    Create a JSON Web Token (JWT) with the specified type and data.

    Parameters
    ----------
    token_type : str
        The type of the token (e.g., 'access', 'refresh') that will be included
        in the JWT payload.
    token_data : dict
        A dictionary containing the data to be included in the JWT payload.
        This data will be merged with the token type in the final JWT.
    expire_minutes : int, optional
        The number of minutes until the token expires. Defaults to
        settings.auth_jwt.access_token_expire_minutes.
    expire_timedelta : timedelta | None, optional
        An optional timedelta object that can be used to specify a custom
        expiration duration. If provided, this will take precedence over
        expire_minutes.

    Returns
    -------
    str
        An encoded JWT as a string.
    """
    jwt_payload = {
        settings.auth_jwt.TOKEN_TIPE_FIELD: token_type,
    }
    jwt_payload.update(token_data)
    return await encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


async def create_access_token(user: schemas.UserSchema):
    """
    Create an access token for a user.

    Parameters
    ----------
    user : UserSchema
        An instance of the UserSchema that contains user information

    Returns
    -------
    str
        An encoded access token as a string.
    """
    jwt_payload = {
        "sub": user.id,
        "username": user.username,
    }
    return await create_jwt(
        token_type=settings.auth_jwt.ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )


async def create_refresh_token(user: schemas.UserSchema):
    """
    Create a refresh token for a user.

    Parameters
    ----------
    user : UserSchema
        An instance of the UserSchema that contains user information

    Returns
    -------
    str
        An encoded refresh token as a string.
    """
    jwt_payload = {
        "sub": user.id,
        "username": user.username,
    }
    return await create_jwt(
        token_type=settings.auth_jwt.REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )


async def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode("utf-8")
    return bcrypt.hashpw(pwd_bytes, salt)


async def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode("utf-8"),
        hashed_password=hashed_password,
    )
