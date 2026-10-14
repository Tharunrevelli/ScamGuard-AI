"""
Automated Integration Tests for ScamGuard Backend API.
Tests endpoints, schemas, validation, error handling, and batch operations.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.anyio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "ScamGuard" in data["service"]
        assert "model_loaded" in data


@pytest.mark.anyio
async def test_v1_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_model_info_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/model-info")
        assert res.status_code == 200
        data = res.json()
        assert "model_version" in data
        assert "training_dataset" in data
        assert "metrics" in data
        assert "accuracy" in data["metrics"]


@pytest.mark.anyio
async def test_detect_phishing_message():
    phishing_text = (
        "URGENT: Chase Bank alert! Your account access has been suspended. "
        "Verify your identity immediately at https://chase-security-verify.xyz/login within 24 hours."
    )
    payload = {
        "text": phishing_text,
        "source": "MANUAL",
        "client_session_id": "test_session_phishing",
        "bypass_prefilter": True,
        "redact_pii_before_analysis": False
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/detect", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["classification"] in ("Likely Scam", "Suspicious")
        assert data["risk_score"] >= 65.0
        assert data["confidence"] > 0.70
        assert len(data["indicators"]) > 0
        assert len(data["suggested_actions"]) > 0
        assert data["stage_applied"] == "HYBRID_REMOTE"


@pytest.mark.anyio
async def test_detect_benign_message():
    benign_text = "Hey Alex, are we still meeting for lunch at 1pm today? Let me know!"
    payload = {
        "text": benign_text,
        "source": "MANUAL",
        "client_session_id": "test_session_benign",
        "bypass_prefilter": True,
        "redact_pii_before_analysis": False
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/detect", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["classification"] == "Likely Safe"
        assert data["risk_score"] < 30.0


@pytest.mark.anyio
async def test_detect_ambiguous_short_message():
    ambiguous_text = "Ok call me"
    payload = {
        "text": ambiguous_text,
        "source": "MANUAL",
        "client_session_id": "test_session_ambiguous",
        "bypass_prefilter": True,
        "redact_pii_before_analysis": False
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/detect", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["classification"] == "Unable to Determine"
        assert data["confidence"] < 0.60


@pytest.mark.anyio
async def test_detect_with_pii_redaction():
    text_with_pii = "Please send OTP to +1-555-234-5678 or email john.doe@secure-bank.com immediately."
    payload = {
        "text": text_with_pii,
        "source": "MANUAL",
        "client_session_id": "test_session_pii",
        "bypass_prefilter": True,
        "redact_pii_before_analysis": True
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/detect", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["pii_redacted"] is True
        assert data["redacted_preview"] is not None
        assert "[PHONE_REDACTED]" in data["redacted_preview"]


@pytest.mark.anyio
async def test_empty_message_validation():
    payload = {"text": "   ", "source": "MANUAL"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/detect", json=payload)
        assert res.status_code == 422  # Unprocessable Entity


@pytest.mark.anyio
async def test_oversized_message_validation():
    payload = {"text": "A" * 4500, "source": "MANUAL"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/detect", json=payload)
        assert res.status_code == 422


@pytest.mark.anyio
async def test_stage1_prefilter_endpoint():
    payload_benign = {"text": "See you at the library soon.", "user_requested": False}
    payload_candidate = {"text": "Urgent notice: Claim $500 reward at https://bit.ly/claim", "user_requested": False}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res1 = await client.post("/api/v1/prefilter-check", json=payload_benign)
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["should_route_to_backend"] is False
        assert data1["local_risk_tier"] == "Likely Safe"

        res2 = await client.post("/api/v1/prefilter-check", json=payload_candidate)
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["should_route_to_backend"] is True
        assert data2["local_risk_tier"] == "Candidate"


@pytest.mark.anyio
async def test_batch_evaluate_endpoint():
    messages = [
        "Hey, are you free for a call?",
        "URGENT: Your account was suspended. Log in at http://bank.xyz/verify",
        "Sounds good, see you at 6pm."
    ]
    payload = {"messages": messages, "use_prefilter": True}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/evaluate-batch", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["total_messages"] == 3
        assert data["filtered_locally"] >= 1
        assert data["routed_to_backend"] >= 1
        assert data["request_reduction_pct"] > 0
