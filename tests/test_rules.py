"""
Unit Tests for Heuristic Rule Engine.
Validates individual indicator categories and score saturation.
"""
import pytest
from backend.app.core.rules import default_rule_engine


def test_empty_text_rule_evaluation():
    res = default_rule_engine.evaluate("")
    assert res["rule_score"] == 0.0
    assert res["matched_count"] == 0
    assert res["rule_classification"] == "Likely Safe"


def test_credential_harvest_critical_trigger():
    text = "Please send your one-time password OTP immediately to verify your account."
    res = default_rule_engine.evaluate(text)
    assert res["has_critical"] is True
    assert res["rule_score"] >= 65.0
    assert any(ind["category"] == "CREDENTIAL_HARVEST" for ind in res["indicators"])


def test_urgency_threat_trigger():
    text = "Action required: Your account is suspended within 24 hours due to unauthorized login activity."
    res = default_rule_engine.evaluate(text)
    assert res["rule_score"] >= 35.0
    assert any(ind["category"] == "URGENCY_THREAT" for ind in res["indicators"])


def test_financial_lottery_lure():
    text = "Congratulations! You have been selected to win a cash prize of $50,000 in our international lottery."
    res = default_rule_engine.evaluate(text)
    assert res["rule_score"] >= 35.0
    assert any(ind["category"] == "FINANCIAL_LURE" for ind in res["indicators"])


def test_suspicious_obfuscated_links():
    text1 = "Visit http://192.168.1.1:8080/secure to verify."
    text2 = "Click here https://bit.ly/free-bonus-claim"
    text3 = "Go to https://bank-login.xyz/update"

    res1 = default_rule_engine.evaluate(text1)
    res2 = default_rule_engine.evaluate(text2)
    res3 = default_rule_engine.evaluate(text3)

    assert any(ind["category"] == "SUSPICIOUS_LINKS" for ind in res1["indicators"])
    assert any(ind["category"] == "SUSPICIOUS_LINKS" for ind in res2["indicators"])
    assert any(ind["category"] == "SUSPICIOUS_LINKS" for ind in res3["indicators"])


def test_benign_conversational_text_no_false_alarm():
    text = "Can you send me the lecture slides from yesterday's database class?"
    res = default_rule_engine.evaluate(text)
    assert res["rule_score"] == 0.0
    assert res["matched_count"] == 0
    assert res["rule_classification"] == "Likely Safe"
