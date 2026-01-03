from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    secret_key: Optional[str] = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"  # Default for dev only
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    qdrant_url: Optional[str] = None
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields that are in the .env file but not in the model


settings = Settings()