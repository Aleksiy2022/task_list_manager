from jwt_auth import jwt_utils
from api.core import schemas
from api.core.config import settings
from datetime import timedelta


async def create_jwt(
        token_type: str,
        token_data: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload = {
        settings.auth_jwt.TOKEN_TIPE_FIELD: token_type,
    }
    jwt_payload.update(token_data)
    return await jwt_utils.encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta
    )


async def create_access_token(user: schemas.UserSchema):
    jwt_payload = {
        "sub": user.id,
        "username": user.username,
    }
    return await create_jwt(
        token_type=settings.auth_jwt.ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )


async def create_refresh_token(user: schemas.UserSchema):
    jwt_payload = {
        "sub": user.id,
        "username": user.username,
    }
    return await create_jwt(
        token_type=settings.auth_jwt.REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days)
    )
