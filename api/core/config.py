import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path.cwd().resolve()
load_dotenv()


class DbSettings(BaseSettings):
    """
    The DbSettings class represents the configuration
    parameters for connecting to a database.

    Attributes
    ----------
    username : str
        The username for connecting to the database.
        Obtained from the environment variable DB_USERNAME.
    password : str
        The password for connecting to the database.
        Obtained from the environment variable DB_PASSWORD.
    host : str
        The database host. Defaults to "db".
    port : str
        The port for connecting to the database.
        Defaults to "5432".
    name : str
        The name of the database. Obtained from the environment
        variable DB_NAME.
    url : str
        The connection string for the database in the
        postgresql+asyncpg format, constructed based on the other
        attributes.

    Notes
    -----
    To properly use this class, it is necessary to set the environment
    variables DB_USERNAME, DB_PASSWORD, and DB_NAME before using it.
    """

    username: str = os.environ.get("DB_USERNAME")
    password: str = os.environ.get("DB_PASSWORD")
    host: str = "db"
    port: str = "5432"
    name: str = os.environ.get("DB_NAME")
    url: str = f"postgresql+asyncpg://{username}:{password}@db:{port}/{name}"


class RedisSettings(BaseSettings):
    """
    Represents the configuration parameters for connecting to
     a Redis database.

    Attributes
    ----------
    redis_password : str
        Password for connecting to Redis. Obtained from the
        environment variable REDIS_PASSWORD.
    username : str
        Username for connecting to Redis. Obtained from the
        environment variable REDIS_USER.
    password : str
        Password of the created user for connecting to Redis.
        Obtained from the environment variable REDIS_USER_PASSWORD.
    port : str
        Port for connecting to Redis. Defaults to "6379".
    host : str
        Host for the Redis database. Defaults to "redis".
    redis_db : str
        The Redis database number. Defaults to "0".
    redis_url : str
        The connection string for Redis in the format
        "redis://<username>:<password>@<host>:<port>/<redis_db>".

    Notes
    -----
    Before using this class, make sure the following environment
    variables are set:
    - REDIS_PASSWORD
    - REDIS_USER
    - REDIS_USER_PASSWORD
    """

    redis_password: str = os.environ.get("REDIS_PASSWORD")
    username: str = os.environ.get("REDIS_USER")
    password: str = os.environ.get("REDIS_USER_PASSWORD")
    port: str = "6379"
    host: str = "redis"
    redis_db: str = "0"
    redis_url: str = f"redis://{username}:{password}@{host}:{port}/{redis_db}"


class AuthJWT(BaseSettings):
    """
    Represents the configuration parameters for JSON Web Token
    (JWT) authentication.

    Attributes
    ----------
    private_key : Path
        The path to the private key used for signing JWTs.
        Defaults to "certs/jwt-private.pem" in the BASE_DIR.
    public_key_path : Path
        The path to the public key used for verifying JWTs.
        Defaults to "certs/jwt-public.pem" in the BASE_DIR.
    algorithm : str
        The algorithm used for signing JWTs. Defaults to "RS256".
    access_token_expire_minutes : int
        The expiration time for access tokens in minutes.
        Defaults to 15.
    refresh_token_expire_days : int
        The expiration time for refresh tokens in days.
        Defaults to 30.
    TOKEN_TYPE_FIELD : str
        The field name used to specify the type of the token.
        Defaults to "type".
    ACCESS_TOKEN_TYPE : str
        The type identifier for access tokens. Defaults to "access".
    REFRESH_TOKEN_TYPE : str
        The type identifier for refresh tokens. Defaults to "refresh".

    Notes
    -----
    Before using this class, ensure that the paths to the private and
    public key files are correct and that the keys are appropriately
    generated and stored in the specified paths.
    """

    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    TOKEN_TIPE_FIELD: str = "type"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"


class Settings(BaseSettings):
    """
    Represents the application's configuration settings,
    incorporating authentication,database, and Redis
    configurations.

    Attributes
    ----------
    auth_jwt : AuthJWT
        The configuration settings for JSON Web Token (JWT)
        authentication. Instantiated by default.
    db_settings : DbSettings
        The configuration settings for the database connection
        and usage. Instantiated by default.
    redis_settings : RedisSettings
        The configuration settings for connecting to and using a
        Redis server. Instantiated by default.

    Notes
    -----
    Ensure that each of the sub-configuration classes (`AuthJWT`,
    `DbSettings`, `RedisSettings`) is properly defined and imported.
    This class combines these settings to facilitate centralized
    management and access to application-level configurations.
    """

    auth_jwt: AuthJWT = AuthJWT()
    db_settings: DbSettings = DbSettings()
    redis_settings: RedisSettings = RedisSettings()


settings = Settings()
