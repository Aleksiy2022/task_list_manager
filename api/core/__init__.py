"""
Package 'core'.

Components of the package.
1. The 'config' module contains the main configurations of the
microblog application.
2. The 'dbhelper' module ensures interaction with the database.
"""

__all__ = (
    "db_helper",
    "settings"
)

from .config import settings
from api.db.dbhelper import db_helper
