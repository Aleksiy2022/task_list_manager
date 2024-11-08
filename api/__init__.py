"""
Package 'api'.

The server part of the web application for managing the task list
and authentication.

Components of the package:
1. The 'core' contains the basic settings for the application,
    database, and Redis.
2. The 'db' contains database connection settings and modules with
    queries for interacting with the database
3. The 'routers' contains logic for processing requests and responses
    to endpoints.
4. The 'dependencies' module contains dependencies that process data received
    by view functions.
5. The 'main' module acts as the central module where the initialization and
    configuration of the web server and its components take place.
6. The 'redis_client' contains connecting to Redis.
"""

__all__ = (
    "settings"
)

from .core import settings
