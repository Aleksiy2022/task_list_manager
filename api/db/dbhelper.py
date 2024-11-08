from asyncio import current_task

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session

from api.core.config import settings


class DataBaseHelper:
    """
    Helper class for working with the database.

    This class provides methods for creating and configuring
    an asynchronous database engine and managed sessions.

    Attributes
    ----------
    engine : AsyncEngine
        The asynchronous database engine created based on the
        provided URL.
    session_factory : async_sessionmaker
        The factory for creating asynchronous sessions.

    Methods
    -------
    init(self, url: str, echo: bool = False)
        Initializes an instance of DatabaseHelper with the specified
        parameters.
    get_scoped_session(self)
        Returns a new managed session associated with the current task.
    """

    def __init__(self, url: str, echo: bool = False) -> None:
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        """
        Return a new managed session associated with the current task.

        Returns
        -------
        async_scoped_session
            The managed session.
        """
        return async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )


db_helper = DataBaseHelper(
    url=settings.db_settings.url
)
