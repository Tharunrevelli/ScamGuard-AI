"""
Explainable Heuristic Rule Engine for Scam & Phishing Detection.
Provides deterministic, interpretable threat signals.
"""
import re
from typing import Dict, List, Any


# Threat Indicators Definitions
INDICATOR_CATEGORIES = {
    "URGENCY_THREAT": {
        "severity": "HIGH",
        "description": "Urgent timeline or threat of account suspension/action",
        "patterns": [
            r"\b(immediately|urgent|urgently|within 24 hours?|action required|suspended|suspension|deactivated|terminated|blocked|restricted)\b",
            r"\b(last warning|final notice|unauthorized (access|login|activity)|security alert|breach detected)\b",
            r"\b(act now|time sensitive|expires today|deadline)\b",
        ],
    },
    "CREDENTIAL_HARVEST": {
        "severity": "CRITICAL",
        "description": "Direct request for passwords, OTPs, PINs, or security verification",
        "patterns": [
            r"\b(one-time password|otp|verification code|security code|passcode|secret pin)\b",
            r"\b(verify your (account|identity|password|pin|card)|confirm your password)\b",
            r"\b(enter your (pin|password|ssn|social security|credentials))\b",
            r"\b(update (kyc|pan card|aadhaar|bank details))\b",
        ],
    },
    "FINANCIAL_LURE": {
        "severity": "HIGH",
        "description": "Unrealistic financial prizes, lottery awards, or cash rewards",
        "patterns": [
            r"\b(won|winner|winning|congratulations,? you (have|ve) been selected)\b",
            r"\b(lottery|jackpot|cash prize|claim your (prize|reward|gift card|bonus))\b",
            r"\b(\$|£|€|₹)\s*\d+([,\.]\d+)?\s*(thousand|million|cash|bonus|award|waiting)\b",
            r"\b(guaranteed returns?|risk-free investment|crypto giveaway|double your (money|bitcoin))\b",
        ],
    },
    "IMPERSONATION": {
        "severity": "MEDIUM",
        "description": "Claims to be an authoritative institution, bank, delivery service, or tax bureau",
        "patterns": [
            r"\b(paypal|netflix|amazon security|apple support|chase bank|wells fargo|bank of america)\b",
            r"\b(irs|hmrc|tax refund|federal reserve|customs (duty|office|clearance))\b",
            r"\b(fedex|dhl|ups|usps|postal service|parcel tracking|delivery failed|package pending)\b",
            r"\b(whatsapp support|customer care team|official security team)\b",
        ],
    },
    "SUSPICIOUS_PAYMENT": {
        "severity": "HIGH",
        "description": "Demands for untraceable payment, advance fees, or gift cards",
        "patterns": [
            r"\b(wire transfer|western union|moneygram|crypto|bitcoin|usdt|gift card)\b",
            r"\b(advance fee|processing fee|clearance fee|refundable deposit)\b",
            r"\b(send money to claim|pay to receive)\b",
        ],
    },
    "SUSPICIOUS_LINKS": {
        "severity": "HIGH",
        "description": "Obfuscated, shortened, or suspicious link structures",
        "patterns": [
            r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?(/.*)?",  # IP-based URL
            r"https?://([a-zA-Z0-9-]+\.)*(bit\.ly|tinyurl\.com|t\.co|is\.gd|cutt\.ly|rb\.gy|shorturl\.at|ow\.ly)/[^\s]+",
            r"https?://[^\s]+\.(xyz|top|tk|club|work|buzz|icu|live|monster|cam|link)/[^\s]*",
            r"https?://[^\s]*(paypa1|arnazon|netf1ix|g00gle|apple-id|secure-login|verify-account)[^\s]*",
        ],
    },
    "CALL_BACK_LURE": {
        "severity": "MEDIUM",
        "description": "Urgent prompt to call a premium or unverified phone number",
        "patterns": [
            r"\b(call now|ring back|call immediately|toll[- ]free|helpline)\b\s*(on|at)?\s*[\+]?[\d\s\-\(\)]{7,15}",
            r"\btext (stop|yes|claim|win) to \d{4,6}\b",
        ],
    },
}


class RuleEngine:
    """Evaluates text against explainable heuristic scam indicators."""

    def __init__(self):
        self.compiled_rules = {}
        for category, data in INDICATOR_CATEGORIES.items():
            compiled = [re.compile(p, re.IGNORECASE) for p in data["patterns"]]
            self.compiled_rules[category] = {
                "severity": data["severity"],
                "description": data["description"],
                "patterns": compiled,
            }

    def evaluate(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return matched indicators, rule score (0-100), and flags.
        """
        if not text or not text.strip():
            return {
                "rule_score": 0.0,
                "matched_count": 0,
                "has_critical": False,
                "indicators": [],
                "rule_classification": "Likely Safe",
            }

        matched_indicators = []
        severity_weights = {"LOW": 10, "MEDIUM": 20, "HIGH": 40, "CRITICAL": 55}
        total_weight = 0.0
        has_critical = False

        for category, rule_info in self.compiled_rules.items():
            category_matched = False
            matched_snippets = []

            for pattern in rule_info["patterns"]:
                matches = pattern.findall(text)
                if matches:
                    category_matched = True
                    for m in matches:
                        match_str = m if isinstance(m, str) else m[0]
                        if match_str and match_str not in matched_snippets:
                            matched_snippets.append(match_str)

            if category_matched:
                sev = rule_info["severity"]
                if sev == "CRITICAL":
                    has_critical = True
                weight = severity_weights.get(sev, 15)
                total_weight += weight
                matched_indicators.append({
                    "category": category,
                    "severity": sev,
                    "description": rule_info["description"],
                    "matched_snippets": matched_snippets[:3],
                })

        # Non-linear score saturation up to 100
        # If critical indicator present (e.g. OTP harvesting), base score starts at least at 60
        rule_score = min(100.0, total_weight * 0.9)
        if has_critical and rule_score < 65.0:
            rule_score = 65.0

        if rule_score >= 65.0 or (has_critical and total_weight >= 50):
            classification = "Likely Scam"
        elif rule_score >= 30.0:
            classification = "Suspicious"
        else:
            classification = "Likely Safe"

        return {
            "rule_score": round(rule_score, 2),
            "matched_count": len(matched_indicators),
            "has_critical": has_critical,
            "indicators": matched_indicators,
            "rule_classification": classification,
        }


# Singleton instance
default_rule_engine = RuleEngine()
