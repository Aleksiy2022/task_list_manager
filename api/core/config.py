import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path.cwd().resolve()
load_dotenv()


class AuthJWT(BaseModel):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    TOKEN_TIPE_FIELD: str = "type"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"


class DbSettings(BaseSettings):
    username: str = os.environ.get("DB_USERNAME")
    password: str = os.environ.get("DB_PASSWORD")
    host: str = os.environ.get("DB_HOST")
    port: str = os.environ.get("DB_PORT")
    name: str = os.environ.get("DB_NAME")
    url: str = (
        f"postgresql+asyncpg://{username}:{password}@db:{port}/{name}"
    )


class RedisSettings(BaseSettings):
    redis_password: str = os.environ.get("REDIS_PASSWORD")
    username: str = os.environ.get("REDIS_USER")
    password: str = os.environ.get("REDIS_USER_PASSWORD")
    port: str = os.environ.get("REDIS_PORT")
    host: str = os.environ.get("REDIS_HOST")

    redis_url: str = f"redis://{username}:{password}@{host}:{port}/0"


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()
    db_settings: DbSettings = DbSettings()
    redis_settings: RedisSettings = RedisSettings()


settings = Settings()
