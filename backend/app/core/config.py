from functools import lru_cache
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized Application Configuration.
    Loads and validates environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "Jeppiaar University ERP"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-64-bytes-min"
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Logging & Observability
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # "text" | "json" | "auto"

    # Database Configuration (PostgreSQL + asyncpg)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "erp_app"
    POSTGRES_PASSWORD: str = "erp_secure_password_123"
    POSTGRES_DB: str = "university_erp"
    DATABASE_URL: Optional[str] = None

    # Connection Pooling & Tuning
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str) and v.strip():
            # Ensure asyncpg driver dialect is used for async SQLAlchemy
            url = v.strip()
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql+psycopg://"):
                return url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
            return url
        
        # Build default async connection string if not provided in environment
        values = info.data
        user = values.get("POSTGRES_USER", "erp_app")
        password = values.get("POSTGRES_PASSWORD", "erp_secure_password_123")
        server = values.get("POSTGRES_SERVER", "localhost")
        port = values.get("POSTGRES_PORT", 5432)
        db = values.get("POSTGRES_DB", "university_erp")
        return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "https://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def validate_log_level(cls, v: Optional[str]) -> str:
        if isinstance(v, str) and v.strip():
            level = v.strip().upper()
            if level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
                return level
        return "INFO"

    @field_validator("LOG_FORMAT", mode="before")
    @classmethod
    def validate_log_format(cls, v: Optional[str]) -> str:
        if isinstance(v, str) and v.strip():
            fmt = v.strip().lower()
            if fmt in ("text", "json", "auto"):
                return fmt
        return "text"

    @property
    def jwt_secret(self) -> str:
        return self.JWT_SECRET_KEY or self.SECRET_KEY


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
