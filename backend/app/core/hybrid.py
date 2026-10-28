"""
Hybrid Scam Detection Engine.
Fuses interpretable heuristic rule signals, calibrated Ensemble ML predictions,
URL & Domain Threat Intelligence, and 6-dimensional threat vector decomposition.
Implements the 4-tier decision taxonomy: Likely Safe | Suspicious | Likely Scam | Unable to Determine.
"""
from typing import Dict, Any, List
from backend.app.core.url_intel import default_url_intel
from backend.app.core.threat_vectors import default_threat_vectors
from backend.app.core.annotator import default_message_annotator


class HybridEngine:
    """Combines rule-based indicators, ML probabilities, and URL intel into calibrated risk assessments."""

    def evaluate(self, text: str, rule_result: Dict[str, Any], ml_result: Dict[str, Any]) -> Dict[str, Any]:
        trimmed = text.strip() if text else ""
        word_count = len(trimmed.split())

        # URL Threat Intelligence Analysis
        url_intel = default_url_intel.analyze(trimmed)
        url_risk = float(url_intel.get("url_risk_score", 0.0))

        # 6-Dimensional Threat Vector Decomposition
        ml_prob = float(ml_result.get("scam_probability", 0.0))
        threat_vectors = default_threat_vectors.compute_vectors(trimmed, ml_prob)

        # Interactive Token Annotation for UI Highlight Spans
        annotated_result = default_message_annotator.annotate(trimmed)

        # Edge case: Empty message
        if not trimmed:
            return {
                "classification": "Likely Safe",
                "risk_score": 0.0,
                "confidence": 1.0,
                "tier": "Likely Safe",
                "reasons": ["Empty message provided"],
                "suggested_actions": ["No action required."],
                "breakdown": {"ml_risk": 0.0, "rule_risk": 0.0, "url_risk": 0.0, "hybrid_weight": "EQUAL"},
                "threat_vectors": threat_vectors,
                "url_intelligence": url_intel,
                "annotated_message": annotated_result,
                "token_attributions": []
            }

        rule_score = float(rule_result.get("rule_score", 0.0))
        ml_score = ml_prob * 100.0
        has_critical = bool(rule_result.get("has_critical", False))
        matched_indicators = rule_result.get("indicators", [])

        # Check for critical URL threat (e.g. brand typosquatting, raw IP)
        has_critical_url = any(
            d.get("severity") == "CRITICAL" or d.get("typosquatting_detected")
            for d in url_intel.get("details", [])
        )
        if has_critical_url:
            has_critical = True

        # Ambiguous edge case: very short message without indicators (1-3 words)
        if word_count <= 3 and rule_score == 0 and ml_score < 40 and url_risk == 0:
            return {
                "classification": "Unable to Determine",
                "risk_score": round(max(ml_score, 15.0), 1),
                "confidence": 0.40,
                "tier": "Unable to Determine",
                "reasons": [
                    "Message is too short to establish statistical or contextual intent.",
                    "No explicit scam indicators or hyperlinks detected."
                ],
                "suggested_actions": [
                    "Request more context from sender if unexpected.",
                    "Do not act on unexpected requests without independent verification."
                ],
                "breakdown": {"ml_risk": round(ml_score, 1), "rule_risk": rule_score, "url_risk": 0.0, "hybrid_weight": "AMBIGUOUS_SHORT"},
                "threat_vectors": threat_vectors,
                "url_intelligence": url_intel,
                "annotated_message": annotated_result,
                "token_attributions": ml_result.get("token_attributions", [])
            }

        # Weighted score fusion
        # If critical indicator present (e.g. OTP harvesting, brand typosquatting URL, urgent account suspension), rule takes precedence
        if has_critical:
            max_threat = max(rule_score, url_risk, 75.0)
            fused_score = 0.35 * ml_score + 0.65 * max_threat
            fused_score = min(100.0, max(fused_score, 70.0))
        else:
            # Three-way balanced fusion: 50% ML probability, 35% Rule Score, 15% URL Threat Score
            fused_score = 0.50 * ml_score + 0.35 * rule_score + 0.15 * url_risk

        fused_score = round(fused_score, 1)

        # Build human-readable forensic explanations
        reasons: List[str] = []
        suggested_actions: List[str] = []

        for ind in matched_indicators:
            snippets = ", ".join([f'"{s}"' for s in ind.get("matched_snippets", [])])
            reasons.append(f"[{ind.get('severity')}] {ind.get('description')} (Found: {snippets})")

        # Add URL findings to reasons
        for u_detail in url_intel.get("details", []):
            if u_detail["risk_score"] >= 30:
                reasons.append(f"[{u_detail['severity']}] URL '{u_detail['raw_url']}': {'; '.join(u_detail['risk_factors'])}")

        if ml_prob >= 0.70:
            reasons.append(f"Production Ensemble identified high vocabulary alignment with verified scam corpora ({ml_prob*100:.1f}% confidence).")
        elif ml_prob <= 0.10 and rule_score == 0 and url_risk == 0:
            reasons.append("Machine learning model identified high lexical similarity to authentic interpersonal communication.")

        # Determine 4-tier classification
        if fused_score >= 65.0 or (has_critical and fused_score >= 55.0):
            classification = "Likely Scam"
            confidence = min(0.99, 0.75 + (fused_score / 400.0))
            suggested_actions = [
                "DO NOT click any embedded links or open attachments in this message.",
                "NEVER disclose one-time passwords (OTP), CVV codes, or banking credentials.",
                "If claiming to be from a bank or shipping company, verify directly via their official app or website.",
                "Block this sender and report the communication as fraudulent."
            ]
        elif fused_score >= 32.0 or (len(matched_indicators) > 0 and ml_prob >= 0.25) or url_risk >= 35.0:
            classification = "Suspicious"
            confidence = 0.68
            suggested_actions = [
                "Exercise caution: this message displays markers frequently observed in smishing or unsolicited lures.",
                "Inspect any embedded sender numbers or domain names carefully before replying.",
                "Do not disclose confidential personal details or transfer funds."
            ]
        elif word_count <= 4 and 20.0 <= fused_score < 32.0:
            classification = "Unable to Determine"
            confidence = 0.50
            suggested_actions = [
                "Insufficient context in message to confirm safety.",
                "Verify sender identity through a trusted secondary channel."
            ]
        else:
            classification = "Likely Safe"
            confidence = max(0.70, 1.0 - (fused_score / 100.0))
            suggested_actions = [
                "No immediate threat vectors detected.",
                "Standard vigilance is advised: remember that familiar contacts can occasionally be compromised."
            ]

        return {
            "classification": classification,
            "risk_score": fused_score,
            "confidence": round(confidence, 2),
            "tier": classification,
            "reasons": reasons if reasons else ["No prominent threat indicators detected."],
            "suggested_actions": suggested_actions,
            "breakdown": {
                "ml_probability": round(ml_prob, 4),
                "ml_risk_score": round(ml_score, 1),
                "rule_risk_score": round(rule_score, 1),
                "url_risk_score": round(url_risk, 1),
                "matched_rule_count": len(matched_indicators),
                "has_critical_indicators": has_critical,
            },
            "threat_vectors": threat_vectors,
            "url_intelligence": url_intel,
            "annotated_message": annotated_result,
            "token_attributions": ml_result.get("token_attributions", [])
        }


default_hybrid_engine = HybridEngine()
