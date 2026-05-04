from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AI News API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ai_news"

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    LLM_PROVIDER: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None

    CRAWLER_INTERVAL_MINUTES: int = 60

    ADMIN_USER_IDS: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
