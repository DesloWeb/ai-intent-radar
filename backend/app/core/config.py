"""Core configuration for AI Smart Intent Radar."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Smart Intent Radar"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/radar"
    DATABASE_TEST_URL: str = "sqlite+aiosqlite:///./test.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "jwt-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # AI Provider
    AI_PROVIDER: str = "mock"  # "anthropic" or "mock"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Scoring Thresholds
    MIN_INTENT_SCORE: float = 0.3
    MIN_CONFIDENCE: float = 0.4
    HIGH_PRIORITY_THRESHOLD: float = 0.7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    @classmethod
    def get_cors_origins(cls) -> list[str]:
        """Get CORS origins from env or defaults."""
        import os
        import json
        env_val = os.getenv("CORS_ORIGINS")
        if env_val:
            try:
                return json.loads(env_val)
            except (json.JSONDecodeError, TypeError):
                pass
        return ["http://localhost:3000", "http://localhost:8000"]

    # Data Sources
    SAM_GOV_API_KEY: Optional[str] = None
    ENABLED_COUNTRIES: list[str] = ["US"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
