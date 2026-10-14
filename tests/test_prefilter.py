"""
Tests for Stage 1 On-Device / Local Prefiltering and Selective Routing.
"""
import pytest
from backend.app.core.prefilter import default_local_prefilter


def test_benign_conversational_filtered_locally():
    samples = [
        "Hey! Are we still grabbing coffee later?",
        "Okay sounds good, see you soon.",
        "Can you send me the homework assignment?",
        "I'm running about 5 minutes late."
    ]
    for text in samples:
        res = default_local_prefilter.evaluate(text, user_requested=False)
        assert res["should_route_to_backend"] is False
        assert res["local_risk_tier"] == "Likely Safe"
        assert res["savings_category"] == "FILTERED_BENIGN_LOCAL"


def test_candidate_message_routed_to_backend():
    candidates = [
        "Your package is delayed. Update address at https://post-tracking.xyz",
        "Winner! You won $10,000 cash bonus today.",
        "URGENT: Your account was suspended. Call immediately."
    ]
    for text in candidates:
        res = default_local_prefilter.evaluate(text, user_requested=False)
        assert res["should_route_to_backend"] is True
        assert res["local_risk_tier"] == "Candidate"
        assert len(res["triggers_detected"]) > 0


def test_user_requested_always_bypasses_filter():
    benign_text = "Hey are we still meeting today?"
    # If user explicitly requested analysis (e.g. manual paste or ShareSheet)
    res = default_local_prefilter.evaluate(benign_text, user_requested=True)
    assert res["should_route_to_backend"] is True
    assert res["local_risk_tier"] == "Candidate"
    assert "USER_EXPLICIT_REQUEST" in res["triggers_detected"]
