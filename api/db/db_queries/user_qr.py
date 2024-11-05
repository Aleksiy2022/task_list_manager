from sqlalchemy.ext.asyncio import AsyncSession
from api.core.models import User
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
    return True if user.id else False


async def get_user_by_username(
        session: AsyncSession,
        username: str
) -> User | bool:
    stmt = select(User).where(User.username == username)
    user = await session.scalar(stmt)
    return user
