"""
Unit Tests for In-Memory Rate Limiter.
"""
import pytest
from backend.app.core.rate_limiter import SlidingWindowRateLimiter


def test_rate_limiter_allows_under_limit():
    limiter = SlidingWindowRateLimiter(limit_per_minute=5)
    for _ in range(5):
        assert limiter.is_allowed("test_client_ok") is True


def test_rate_limiter_blocks_over_limit():
    limiter = SlidingWindowRateLimiter(limit_per_minute=3)
    assert limiter.is_allowed("test_client_block") is True
    assert limiter.is_allowed("test_client_block") is True
    assert limiter.is_allowed("test_client_block") is True
    # 4th request exceeds limit of 3
    assert limiter.is_allowed("test_client_block") is False
