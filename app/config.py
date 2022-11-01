from datetime import timedelta
from pathlib import Path

from pydantic import Field, BaseSettings

BASE_DIR = Path(__name__).parent.parent


class Settings(BaseSettings):
    JWT_ALG: str = "HS256"
    JWT_EXP: timedelta = timedelta(minutes=15)
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DB_CONNECTION_STRING: str = Field(..., env="DB_CONNECTION_STRING")
    DEBUG: bool = Field(default=False, env="DEBUG")
    DEFAULT_PAGE_SIZE: int = Field(default=50, env="DEFAULT_PAGE_SIZE")

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
