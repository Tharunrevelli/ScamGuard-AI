"""
Backend Configuration and Environment Settings.
"""
import os
from pydantic import BaseModel


class Settings(BaseModel):
    APP_NAME: str = "ScamGuard AI Detection Engine"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["*"]  # Restrict in production
    RATE_LIMIT_PER_MINUTE: int = 120
    MAX_MESSAGE_LENGTH: int = 4000  # Prevent DoS via oversized payloads
    MIN_MESSAGE_LENGTH: int = 1
    DB_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "scamguard_audit.db")


settings = Settings()
