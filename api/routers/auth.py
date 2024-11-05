from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form
from api.dependencies import scoped_session_db, validate_auth_user
from api.db import user_qr
from api.core import schemas
from jwt_auth import jwt_utils


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
        return {"result": "Invalid data"}
    else:
        return {"result": f"Hello, {username.capitalize()}!"}


@router.post("/login", response_model=schemas.TokenInfo)
async def login_user(
        user: schemas.UserSchema = Depends(validate_auth_user),
):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
    }
    acceess_token = await jwt_utils.encode_jwt(
        payload=jwt_payload
    )
    return schemas.TokenInfo(
        access_token=acceess_token,
        token_type="Bearer"
    )
