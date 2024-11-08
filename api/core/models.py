from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    An abstract base class for all declarative models.
    """


class User(Base):
    """
    The User class represents a user in the database.
    This class maps to the users table.

    Attributes
    ----------
    id : int
      The primary key for the user.
    username : str
      The username of the user.
    password_hash : str
      The hashed password of the user.
    tasks : List[Task]
      A relationship attribute that holds a list of
      tasks associated with the user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[bytes] = mapped_column(nullable=False)
    tasks: Mapped[List["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    """
    The Task class represents a task in the database.
    It extends the Base and maps to the tasks table.

    Attributes
    ----------
    id : int
      The primary key for the task.
    title : str
      The title of the task.
    description : str
      A description of the task.
    status : TaskStatus
      The current status of the task.
    user_id : int
      A foreign key mapped column referring to the user's ID
      in the users table.
    user : User
      A relationship attribute that connects the task to the user
      it belongs to.
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="tasks")
