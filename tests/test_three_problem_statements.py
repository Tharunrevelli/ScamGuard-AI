"""
Unit and Integration Tests for the Three Defense Committee Problem Statements:
1. Content Truncation & Preview Incompleteness Mitigation.
2. High-Volume E-Commerce / Noise Notification Rejection.
3. Multi-Channel Ingestion when Notifications are OFF (SMS, WhatsApp, Gmail) + Contact Whitelist Privacy Shield.
"""
import time
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.prefilter import default_local_prefilter

client = TestClient(app)


# =========================================================================
# Problem Statement 1: Content Truncation & Preview Incompleteness
# =========================================================================

def test_truncation_detection_on_clipped_notification():
    """Verify clipped notification previews (e.g. ending in ellipsis) are flagged."""
    clipped_text = "Chase Alert: Suspicious transaction of $4,500 detected on your debit card. Log in to verify at https://chase-security.cc/auth..."
    is_trunc, warning = default_local_prefilter.check_truncation(clipped_text)
    assert is_trunc is True
    assert "ellipsis" in warning.lower()

    # Via API detection endpoint
    response = client.post("/api/v1/detect", json={
        "text": clipped_text,
        "source": "NOTIFICATION"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_truncated"] is True
    assert data["truncation_warning"] is not None
    assert any("truncated" in r.lower() for r in data["reasons"])


def test_full_message_via_share_sheet_bypasses_truncation():
    """Full unclipped messages sent via Share Sheet or Manual Paste are not flagged as truncated."""
    full_text = "Chase Alert: Suspicious transaction of $4,500 detected on your debit card. Log in to verify at https://chase-security.cc/auth. If this was not you, call fraud department."
    is_trunc, warning = default_local_prefilter.check_truncation(full_text)
    assert is_trunc is False
    assert warning is None

    response = client.post("/api/v1/detect", json={
        "text": full_text,
        "source": "SHARE_SHEET"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_truncated"] is False
    assert data["classification"] in ("Suspicious", "Likely Scam")


# =========================================================================
# Problem Statement 2: High-Volume E-Commerce & Notification Noise Rejection
# =========================================================================

def test_noise_package_rejection_speed_and_accuracy():
    """Verify that e-commerce and food delivery apps are rejected instantly (<0.1 ms)."""
    noise_apps = [
        "com.amazon.mShop.android.shopping",
        "in.amazon.mShop.android.shopping",
        "com.flipkart.android",
        "com.meesho.supply",
        "com.myntra.android",
        "com.ril.ajio",
        "com.application.zomato",
        "in.swiggy.android",
        "com.instagram.android"
    ]
    for pkg in noise_apps:
        t0 = time.perf_counter()
        res = default_local_prefilter.evaluate(
            text="Flash sale 50% off on all items! Buy now before stock runs out.",
            package_name=pkg
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert res["should_route_to_backend"] is False
        assert res["savings_category"] == "FILTERED_NOISE_PACKAGE"
        assert elapsed_ms < 0.5  # Sub-millisecond local rejection


def test_approved_messaging_apps_not_rejected_as_noise():
    """Legitimate interpersonal communication channels must never be dropped as noise."""
    comm_apps = [
        "com.whatsapp",
        "com.google.android.apps.messaging",
        "org.telegram.messenger",
        "com.google.android.gm"
    ]
    for pkg in comm_apps:
        assert default_local_prefilter.is_noise_package(pkg) is False


# =========================================================================
# Problem Statement 3: Multi-Channel Passive Monitoring When Notifications OFF
# =========================================================================

def test_sms_telephony_broadcast_channel():
    """Simulate SMS broadcast receiver ingestion when notifications are disabled."""
    sms_threat = "WELLS FARGO ALERT: Your card has been temporarily locked. Restore access: https://wellsfargo-verify.cc"
    response = client.post("/api/v1/detect", json={
        "text": sms_threat,
        "source": "SMS_BROADCAST",
        "is_sender_in_contacts": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] > 60.0
    assert data["classification"] in ("Suspicious", "Likely Scam")


def test_gmail_api_ingestion_channel():
    """Simulate Gmail OAuth2 API background fetch when phone notifications are disabled."""
    email_threat = "Tax Refund Department: You have an outstanding unclaimed tax refund of $1,250. Click http://irs-tax-refund.top to claim."
    response = client.post("/api/v1/detect", json={
        "text": email_threat,
        "source": "GMAIL_API",
        "is_sender_in_contacts": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] > 60.0
    assert data["classification"] in ("Suspicious", "Likely Scam")


def test_whatsapp_companion_ingestion_channel():
    """Simulate WhatsApp companion multi-device sync when notifications are disabled."""
    whatsapp_threat = "Hi Mom, my phone broke and I am on my friend's number. Please wire $500 immediately to this account."
    response = client.post("/api/v1/detect", json={
        "text": whatsapp_threat,
        "source": "WHATSAPP_COMPANION",
        "is_sender_in_contacts": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 25.0
    assert data["classification"] in ("Suspicious", "Likely Scam")


def test_contact_address_book_privacy_shield_skips_private_chat():
    """
    Privacy Shield: Benign chat from a verified contact in user's address book
    must be resolved locally with zero risk and 0 cloud transmission.
    """
    private_chat = "Hey, are you free this weekend? Let's catch up over coffee."
    response = client.post("/api/v1/detect", json={
        "text": private_chat,
        "source": "WHATSAPP_COMPANION",
        "is_sender_in_contacts": True,
        "bypass_prefilter": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Likely Safe"
    assert data["risk_score"] <= 5.0
    assert data["breakdown"].get("stage1_filtered") is True
    assert data["breakdown"].get("savings_category") == "FILTERED_VERIFIED_CONTACT"


def test_malicious_link_from_compromised_contact_is_not_whitelisted():
    """
    Security invariant: If an attacker takes over a contact's account and sends a phishing URL,
    the contact whitelist is revoked and the message is escalated to Stage 2.
    """
    malicious_from_friend = "Hey check out this crazy video of you: http://malicious-phishing-login.xyz/video"
    res = default_local_prefilter.evaluate(
        text=malicious_from_friend,
        in_contacts=True
    )
    # Must NOT be whitelisted because it contains a URL
    assert res["should_route_to_backend"] is True
    assert "URL_PRESENT" in res["triggers_detected"]
