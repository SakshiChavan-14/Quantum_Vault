
import json
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "QuantumVault API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str = "localhost"
    COOKIE_PATH: str = "/"
    DATABASE_URL: str = "mysql+pymysql://root@127.0.0.1:3306/quantumvault"
    CRYPTO_MASTER_KEY: str = "k8rW6H6j-B1mX8k9_rQ3s5T7u9v1w3x5y7z9A1B3C5E="
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:3000"]

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if not v or not (v.startswith("mysql+pymysql://") or v.startswith("mysql://")):
            raise ValueError(f"Invalid DATABASE_URL: '{v}'. Must be a valid MySQL connection string (mysql+pymysql://).")
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
