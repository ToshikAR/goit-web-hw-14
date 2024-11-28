import logging
from typing import Any
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator, EmailStr

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(module)s - %(message)s")


class Settings(BaseSettings):
    SQLALCHEMY_DB_URL: str = "postgresql+psycopg2"
    MYSQ_DB_URL: str = "mysql+aiomysql"
    SECRET_KEY_JWT: str = "123456789"
    ALGORITHM: str = "qwertyuiop"

    MAIL_USERNAME: EmailStr = "postgres@meail.com"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: str = "user"
    MAIL_PORT: int = 46456
    MAIL_SERVER: str = "server"
    MAIL_FROM_NAME: str = "Systems"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    CLOUDINARY_NAME: str = "qwert"
    CLOUDINARY_API_KEY: int = "1234567"
    CLOUDINARY_API_SECRET: str = "q1w2e3r4t5"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


conf = Settings()
