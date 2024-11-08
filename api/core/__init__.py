"""
Package 'core'.

Components of the package.
1. The 'config' module contains the main configurations
    of the api, database, redis.
2. The 'models' module contains models for creating
    tables and records.
3. The 'schemas' module contains schemas to validate the
    transmitted data and send a response.
"""

__all__ = (
    "db_helper",
    "settings",
    "models",
    "schemas",
)

from api.db.dbhelper import db_helper

from . import models, schemas
from .config import settings
