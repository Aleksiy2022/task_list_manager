from sqlalchemy.ext.asyncio import AsyncSession
from api.core.models import User
from api.core import schemas
from sqlalchemy import select


async def create_user(
        session: AsyncSession,
        username: str,
        password_hash: bytes,
) -> bool:
    """
    Create a new user in the database with the specified username
    and password hash.

    Parameters
    ----------
    session : AsyncSession
        An active SQLAlchemy asynchronous session used for database operations.
    username : str
        The desired username for the new user account.
    password_hash : bytes
        A byte sequence representing the hashed password for securing the user's account.

    Returns
    -------
    bool
        True if the user was successfully created and a valid user ID was assigned;
        otherwise, False.
    """
    user = User(
        username=username,
        password_hash=password_hash,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return True if user.id else False


async def get_user_by_id(
        session: AsyncSession,
        id: int,
) -> schemas.UserSchema | None:
    """
    Retrieve a user from the database by their unique user ID.

    Parameters
    ----------
    session : AsyncSession
        An active SQLAlchemy asynchronous session used for database operations.
    id : int
        The unique identifier of the user to be retrieved.

    Returns
    -------
    UserSchema or None
    """
    stmt = select(User).where(User.id == id)
    user = await session.scalar(stmt)
    return user


async def get_user_by_username(
        session: AsyncSession,
        username: str,
) -> schemas.UserSchema | None:
    """
    Retrieve a user from the database by their username.

    Parameters
    ----------
    session : AsyncSession
        An active SQLAlchemy asynchronous session used for database operations.
    username : str
        The username of the user to be retrieved.

    Returns
    -------
    UserSchema or None
    """
    stmt = select(User).where(User.username == username)
    user = await session.scalar(stmt)
    return user
