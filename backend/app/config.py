"""
Backend Configuration and Environment Settings.
"""
import os
from pydantic import BaseModel


def _resolve_db_path() -> str:
    # Explicit override takes priority
    if os.environ.get("DB_PATH"):
        return os.environ["DB_PATH"]
    # In serverless environments (Vercel, AWS Lambda), write to ephemeral /tmp directory
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "/tmp/scamguard_audit.db"
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "scamguard_audit.db")


class Settings(BaseModel):
    APP_NAME: str = "ScamGuard AI Detection Engine"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["*"]  # Restrict in production
    RATE_LIMIT_PER_MINUTE: int = 120
    MAX_MESSAGE_LENGTH: int = 4000  # Prevent DoS via oversized payloads
    MIN_MESSAGE_LENGTH: int = 1
    DB_PATH: str = _resolve_db_path()


settings = Settings()
