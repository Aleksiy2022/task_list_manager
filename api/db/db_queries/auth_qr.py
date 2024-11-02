from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User
from sqlalchemy import select


async def create_user(
        session: AsyncSession,
        username: str,
        password_hash: bytes,
) -> bool:
    user = User(
        username=username,
        password_hash=password_hash,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    print("******************")
    print(password_hash)
    print("******************")
    return True if user.id else False
