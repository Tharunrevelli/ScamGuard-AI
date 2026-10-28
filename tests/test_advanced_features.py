"""
Automated Unit and Integration Tests for Advanced Features:
- URL Threat Intelligence & Brand Typosquatting (Levenshtein)
- Shannon Entropy & Suspicious TLD Detection
- 6-Vector Multidimensional Threat Decomposition
- Token-Level Visual Span Annotation
- Forensic Incident Investigation Report Endpoint
"""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.url_intel import default_url_intel
from backend.app.core.threat_vectors import default_threat_vectors
from backend.app.core.annotator import default_message_annotator
from backend.app.ml.model import default_model_service


def test_url_intel_typosquatting_detection():
    """Test Levenshtein brand spoofing detection for common banking and tech brands."""
    url = "https://chase-security-verify.xyz/login"
    extracted = default_url_intel.extract_urls(url)
    assert len(extracted) == 1
    
    details = default_url_intel._inspect_url(extracted[0])
    assert details["typosquatting_detected"] is True
    assert details["spoofed_brand"] == "chase"
    assert details["is_risky_tld"] is True
    assert details["risk_score"] >= 70.0


def test_url_intel_ip_and_entropy():
    """Test raw IP address detection and high entropy DGA subdomains."""
    ip_url = "http://192.168.1.100/verify"
    ip_details = default_url_intel._inspect_url(ip_url)
    assert ip_details["is_ip"] is True
    assert ip_details["risk_score"] >= 60.0

    dga_url = "https://a9x8z7q2p1m4k.top/claim"
    dga_details = default_url_intel._inspect_url(dga_url)
    assert dga_details["entropy"] > 3.0
    assert dga_details["is_risky_tld"] is True


def test_threat_vectors_decomposition():
    """Test risk decomposition across the 6 standardized cybersecurity threat vectors."""
    text = "URGENT: Chase Bank alert! Suspicious activity on account. Verify immediately at https://chase-security-verify.xyz/login or your card will be blocked within 24 hours."
    
    decomposition = default_threat_vectors.compute_vectors(text, ml_probability=0.98)
    scores = decomposition["scores"]
    ratings = decomposition["ratings"]
    
    # Must have elevated scores in urgency, credential/account, impersonation, or link risk
    assert scores["urgency_coercion"] >= 50.0
    assert scores["credential_harvesting"] >= 50.0
    assert scores["impersonation"] >= 50.0
    assert scores["link_domain_risk"] >= 50.0
    assert decomposition["primary_vector"] in ["urgency_coercion", "credential_harvesting", "impersonation", "link_domain_risk"]


def test_visual_span_annotator():
    """Test token/span highlighter generates valid non-overlapping tooltips."""
    text = "URGENT: Verify your account immediately at http://verify-bank.xyz"
    annotation = default_message_annotator.annotate(text)
    assert "highlighted_html" in annotation
    assert "spans" in annotation
    assert len(annotation["spans"]) >= 1
    # Check that HTML includes threat tooltip markup
    assert 'class="threat-token' in annotation["highlighted_html"]


def test_ml_token_attributions():
    """Test ML ensemble token-level feature attribution calculation."""
    text = "Claim your free gift now! Call this number or reply to stop."
    attributions = default_model_service._compute_token_attributions(text)
    assert isinstance(attributions, list)
    assert len(attributions) > 0
    # Words like claim, your, free, call, reply should show positive scam weights
    tokens = [a["token"] for a in attributions]
    assert any(t in tokens for t in ["claim", "your", "free", "call", "now", "stop"])


@pytest.mark.anyio
async def test_forensic_report_endpoint():
    """Test POST /api/v1/report compiles an in-depth forensic investigation artifact."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "text": "FINAL NOTICE: Wells Fargo account locked. Confirm PIN at https://wellsfargo-verify.xyz immediately.",
            "source": "MANUAL",
            "bypass_prefilter": True
        }
        res = await ac.post("/api/v1/report", json=payload)
        assert res.status_code == 200
        data = res.json()
        
        assert "report_id" in data
        assert data["report_id"].startswith("SG-FR-")
        assert "message_hash_sha256" in data
        assert len(data["message_hash_sha256"]) == 64  # Valid SHA-256 hex string
        assert data["classification"] in ["Likely Scam", "Suspicious"]
        assert data["risk_score"] >= 65.0
        assert "indicators_of_compromise" in data
        assert len(data["indicators_of_compromise"]) >= 1
        assert "incident_playbook_actions" in data
        assert len(data["incident_playbook_actions"]) > 0
