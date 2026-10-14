"""
In-Memory Sliding Window Rate Limiter.
Protects endpoints against brute force and denial of service without heavy external infrastructure.
"""
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request, status
from backend.app.config import settings


class SlidingWindowRateLimiter:
    """Tracks client request timestamps within a 60-second sliding window."""

    def __init__(self, limit_per_minute: int = 120):
        self.limit_per_minute = limit_per_minute
        self.window_seconds = 60.0
        self.client_requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old timestamps
        timestamps = [t for t in self.client_requests[client_id] if t > cutoff]
        self.client_requests[client_id] = timestamps

        if len(timestamps) >= self.limit_per_minute:
            return False

        self.client_requests[client_id].append(now)
        return True

    def check_request(self, request: Request):
        """Dependency for FastAPI route handlers."""
        client_ip = request.client.host if request.client else "unknown_client"
        if not self.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait a moment before sending additional detection requests.",
                headers={"Retry-After": "30"}
            )


default_rate_limiter = SlidingWindowRateLimiter(settings.RATE_LIMIT_PER_MINUTE)
