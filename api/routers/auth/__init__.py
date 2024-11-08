"""
Package 'auth'.

Components of the package.
1. The 'auth' module provides logic for processing URL
    requests with the 'auth' prefix.
2. The 'auth_helper' module contains functions for creating jwt.
3. The 'jwt_utils' contains functions for encoding and decoding jwt.
"""

__all__ = (
    "router",
)

from .auth import router
