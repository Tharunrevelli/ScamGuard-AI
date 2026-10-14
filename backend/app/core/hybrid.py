"""
Hybrid Scam Detection Engine.
Fuses interpretable heuristic rule signals with calibrated Machine Learning predictions.
Implements the 4-tier decision taxonomy: Likely Safe | Suspicious | Likely Scam | Unable to Determine.
"""
from typing import Dict, Any, List


class HybridEngine:
    """Combines rule-based indicators and ML probabilities into calibrated risk assessments."""

    def evaluate(self, text: str, rule_result: Dict[str, Any], ml_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize Rule Engine results and ML Classifier output.
        """
        trimmed = text.strip() if text else ""
        word_count = len(trimmed.split())

        # Edge case: Empty or extremely short ambiguous text
        if not trimmed:
            return {
                "classification": "Likely Safe",
                "risk_score": 0.0,
                "confidence": 1.0,
                "tier": "Likely Safe",
                "reasons": ["Empty message provided"],
                "suggested_actions": ["No action required."],
                "breakdown": {"ml_risk": 0.0, "rule_risk": 0.0, "hybrid_weight": "EQUAL"},
            }

        rule_score = float(rule_result.get("rule_score", 0.0))
        ml_prob = float(ml_result.get("scam_probability", 0.0))
        ml_score = ml_prob * 100.0
        has_critical = bool(rule_result.get("has_critical", False))
        matched_indicators = rule_result.get("indicators", [])

        # Ambiguous edge case: very short message without indicators (1-3 words)
        if word_count <= 3 and rule_score == 0 and ml_score < 40:
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
                "breakdown": {"ml_risk": round(ml_score, 1), "rule_risk": rule_score, "hybrid_weight": "AMBIGUOUS_SHORT"},
            }

        # Weighted score fusion
        # If critical indicator present (e.g. OTP harvesting, urgent account suspension), rule takes precedence
        if has_critical:
            fused_score = 0.40 * ml_score + 0.60 * max(rule_score, 75.0)
            fused_score = min(100.0, max(fused_score, 70.0))
        else:
            # Balanced fusion: 55% ML probability, 45% Rule Score
            fused_score = 0.55 * ml_score + 0.45 * rule_score

        fused_score = round(fused_score, 1)

        # Build human-readable explanations
        reasons: List[str] = []
        suggested_actions: List[str] = []

        for ind in matched_indicators:
            snippets = ", ".join([f'"{s}"' for s in ind.get("matched_snippets", [])])
            reasons.append(f"[{ind.get('severity')}] {ind.get('description')} (Found: {snippets})")

        if ml_prob >= 0.70:
            reasons.append(f"Machine learning model identified strong vocabulary alignment with known scam corpora ({ml_prob*100:.1f}% confidence).")
        elif ml_prob <= 0.10:
            reasons.append("Machine learning model identified high lexical similarity to legitimate interpersonal communication.")

        # Determine 4-tier classification
        if fused_score >= 65.0 or (has_critical and fused_score >= 55.0):
            classification = "Likely Scam"
            confidence = min(0.99, 0.75 + (fused_score / 400.0))
            suggested_actions = [
                "DO NOT click any links or download attachments in this message.",
                "NEVER disclose one-time passwords (OTP), banking credentials, or personal identity numbers.",
                "Block this sender and report the message as spam/fraud.",
                "If the message claims to be from a bank or service you use, verify independently by opening their official app or website directly."
            ]
        elif fused_score >= 32.0 or (len(matched_indicators) > 0 and ml_prob >= 0.25):
            classification = "Suspicious"
            confidence = 0.68
            suggested_actions = [
                "Exercise caution: this message displays characteristics often associated with unsolicited marketing or deceptive lures.",
                "Inspect any embedded sender numbers or domain names carefully.",
                "Do not reply with sensitive details or send funds."
            ]
        elif word_count <= 4 and 20.0 <= fused_score < 32.0:
            classification = "Unable to Determine"
            confidence = 0.50
            suggested_actions = [
                "Insufficient context in message to confirm safety.",
                "Verify sender identity through a trusted alternative channel."
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
                "matched_rule_count": len(matched_indicators),
                "has_critical_indicators": has_critical,
            },
        }


default_hybrid_engine = HybridEngine()
