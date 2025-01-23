import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "HolyVoice"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    FERNET_KEY: str = secrets.token_urlsafe(32)

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None  # Will be built from components

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = ""
    REDIS_DB: int = 0

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()      