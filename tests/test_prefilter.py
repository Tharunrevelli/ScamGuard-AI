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


def test_noise_package_rejection():
    """Verify high-volume shopping, e-commerce, and social notification packages are rejected locally."""
    noise_pkgs = [
        "com.meesho.supply",
        "in.amazon.mShop.android.shopping",
        "com.amazon.mShop.android.shopping",
        "com.flipkart.android",
        "com.myntra.android",
        "com.ril.ajio",
        "com.application.zomato",
        "in.swiggy.android",
        "com.instagram.android"
    ]
    for pkg in noise_pkgs:
        assert default_local_prefilter.is_noise_package(pkg) is True

    # Legitimate communication channels should not be flagged as noise packages
    comm_pkgs = [
        "com.whatsapp",
        "com.google.android.apps.messaging",
        "org.telegram.messenger",
        "com.google.android.gm"
    ]
    for pkg in comm_pkgs:
        assert default_local_prefilter.is_noise_package(pkg) is False


def test_notification_truncation_detection():
    """Verify clipped notification previews (e.g. ending in ellipsis '...') are detected."""
    truncated_samples = [
        "Your Chase account has been blocked due to suspicious activity. Verify at https://chase-verify.xyz/login...",
        "USPS package pending delivery fee. Update address at http://usps-parcel.top/track…",
        "SECURITY NOTICE: Your email account has been compromised. Log in immediately to verify your identity before it is perm"
    ]
    for sample in truncated_samples:
        is_trunc, warning = default_local_prefilter.check_truncation(sample)
        assert is_trunc is True
        assert warning is not None

    clean_sample = "Hey Sarah! Are we still having lunch at 1pm today? Let me know."
    is_trunc, warning = default_local_prefilter.check_truncation(clean_sample)
    assert is_trunc is False
    assert warning is None
