"""
Privacy & Security Tests.
Verifies data minimization, PII redaction, zero raw-text storage, and session isolation.
"""
import uuid
import pytest
from backend.app.core.privacy import default_privacy_guard
from backend.app.db.database import default_db_manager


def test_pii_redaction_preserves_scam_indicators():
    raw_message = (
        "Urgent: Contact support at +1-800-555-0199 or email alert@bank-security.com "
        "with your card 4111-2222-3333-4444 to prevent account closure at https://bank-verify.xyz."
    )
    redacted, counts = default_privacy_guard.redact_pii(raw_message)

    # Identifiers masked
    assert "[PHONE_REDACTED]" in redacted
    assert "[CARD_NUMBER_REDACTED]" in redacted
    assert "alert@bank-security.com" not in redacted  # user part masked
    assert "@bank-security.com" in redacted

    # Threat indicators preserved for classification
    assert "Urgent:" in redacted
    assert "https://bank-verify.xyz" in redacted
    assert "account closure" in redacted


def test_zero_raw_text_persistence():
    session_seed = f"test_privacy_{uuid.uuid4()}"
    session_hash = default_privacy_guard.generate_session_token(session_seed)
    req_id = f"test_req_{uuid.uuid4()}"

    ok = default_db_manager.record_detection(
        request_id=req_id,
        session_hash=session_hash,
        source="MANUAL",
        classification="Likely Scam",
        risk_score=88.5,
        model_version="v1.0.0-test",
        latency_ms=3.4
    )
    assert ok is True

    # Retrieve history
    history = default_db_manager.get_history_by_session(session_hash)
    assert len(history) > 0
    saved_record = next(r for r in history if r["request_id"] == req_id)

    # Verify no message text exists in the database schema
    assert "text" not in saved_record
    assert "body" not in saved_record
    assert "message" not in saved_record
    assert saved_record["classification"] == "Likely Scam"
    assert saved_record["risk_score"] == 88.5


def test_session_isolation_and_deletion():
    user1_hash = default_privacy_guard.generate_session_token(f"user_1_{uuid.uuid4()}")
    user2_hash = default_privacy_guard.generate_session_token(f"user_2_{uuid.uuid4()}")
    req1 = f"req_{uuid.uuid4()}"
    req2 = f"req_{uuid.uuid4()}"

    default_db_manager.record_detection(req1, user1_hash, "MANUAL", "Likely Safe", 5.0, "v1", 2.0)
    default_db_manager.record_detection(req2, user2_hash, "MANUAL", "Likely Scam", 90.0, "v1", 2.0)

    # User 1 cannot see User 2's audit records
    u1_records = default_db_manager.get_history_by_session(user1_hash)
    assert all(r["request_id"] != req2 for r in u1_records)

    # Deletion only clears User 1
    deleted = default_db_manager.delete_history_by_session(user1_hash)
    assert deleted >= 1

    u1_after = default_db_manager.get_history_by_session(user1_hash)
    assert len(u1_after) == 0

    u2_after = default_db_manager.get_history_by_session(user2_hash)
    assert len(u2_after) > 0  # User 2 intact
