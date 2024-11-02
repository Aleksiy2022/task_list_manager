from typing import Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.dbhelper import db_helper


async def scoped_session_db() -> AsyncGenerator[AsyncSession, None]:
    session = db_helper.get_scoped_session()
    try:
        yield session
    finally:
        await session.close()
