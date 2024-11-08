from datetime import datetime, timedelta, timezone

import jwt

from api import settings


async def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    """
    Encode a JSON Web Token (JWT) using a given payload and private key.

    Parameters
    ----------
    payload : dict
        The payload (claims) to include in the JWT.
    private_key : str
        The private key used to sign the token.
    algorithm : str
        The algorithm used for encoding the JWT.
    expire_minutes : int
        The number of minutes before the token expires.
    expire_timedelta : timedelta, optional
        A `timedelta` object specifying a custom expiration time for the token.

    Returns
    -------
    str
        The encoded JWT as a string.
    """
    to_encode = payload.copy()

    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


async def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    """
    Decode a JSON Web Token (JWT) using a specified public key and algorithm.

    Parameters
    ----------
    token : str or bytes
        The JWT token to decode.
    public_key : str
        The public key used to verify the token's signature.
    algorithm : str
        The algorithm used for encoding the JWT.

    Returns
    -------
    dict
        The decoded payload of the JWT as a dictionary containing the claims.
    """
    decode = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decode
