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
    access_token_expire_minutes: int = 1
    refresh_token_expire_days: int = 30
    TOKEN_TIPE_FIELD: str = "type"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"


class DbSettings(BaseSettings):
    username: str | None = os.environ.get("DB_USERNAME")
    password: str | None = os.environ.get("DB_PASSWORD")
    host: str | None = os.environ.get("DB_HOST")
    port: str | None = os.environ.get("DB_PORT")
    name: str | None = os.environ.get("DB_NAME")
    url: str = (
        f"postgresql+asyncpg://{username}:{password}@db:{port}/{name}"
    )


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()
    db_settings: DbSettings = DbSettings()


settings = Settings()
