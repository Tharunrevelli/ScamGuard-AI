"""
Stage 1 On-Device / Edge Prefilter Module.
Performs inexpensive, explainable local heuristic checks on eligible message content.
Determines whether an event should trigger a backend request (candidate) or stay on device (benign).
"""
import re
from typing import Dict, Any, List


class LocalPrefilter:
    """
    Lightweight prefilter designed to run on the client device (Android/Local).
    Filters out common conversational benign text to save network bandwidth and protect privacy.
    """

    def __init__(self):
        # Quick triggers indicating potential risk that warrants Stage 2 deep analysis
        self.url_pattern = re.compile(
            r"https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|org|net|info|biz|xyz|top|ru|cn|in|uk|io)/[^\s]*",
            re.IGNORECASE
        )
        self.money_pattern = re.compile(
            r"(\$|£|€|₹|rs\.?|inr|usd)\s*\d+|\b\d+\s*(dollars|pounds|euros|rupees|cash|credits|points)\b",
            re.IGNORECASE
        )
        self.urgent_keywords = re.compile(
            r"\b(urgent|immediately|action required|suspended|blocked|warning|compromised|expire[sd]?|otp|code|pin|verify|won|winner|lottery|prize|refund|kyc|bank|card|account)\b",
            re.IGNORECASE
        )
        self.action_call_pattern = re.compile(
            r"\b(call|click|login|sign in|visit|dial|text|reply|send|claim|collect)\b",
            re.IGNORECASE
        )

    def evaluate(self, text: str, user_requested: bool = False) -> Dict[str, Any]:
        """
        Evaluate if a message should be routed to Stage 2 backend analysis.
        If user_requested is True (e.g. user manually pasted or clicked share), always route to Stage 2.
        """
        if not text or not text.strip():
            return {
                "should_route_to_backend": False,
                "local_risk_tier": "Likely Safe",
                "triggers_detected": [],
                "reason": "Empty message",
                "savings_category": "FILTERED_EMPTY",
            }

        # User-initiated analysis always bypasses local filter
        if user_requested:
            return {
                "should_route_to_backend": True,
                "local_risk_tier": "Candidate",
                "triggers_detected": ["USER_EXPLICIT_REQUEST"],
                "reason": "User explicitly requested analysis",
                "savings_category": "USER_REQUESTED",
            }

        triggers: List[str] = []

        # 1. URL check
        if self.url_pattern.search(text):
            triggers.append("URL_PRESENT")

        # 2. Monetary lure check
        if self.money_pattern.search(text):
            triggers.append("FINANCIAL_PATTERN")

        # 3. High-risk urgency / credential / account keywords
        keyword_matches = self.urgent_keywords.findall(text)
        if keyword_matches:
            triggers.append(f"KEYWORDS_FOUND({len(keyword_matches)})")

        # 4. Action prompt combined with suspicious trigger
        if self.action_call_pattern.search(text) and (triggers or len(text) > 200):
            triggers.append("CALL_TO_ACTION")

        # Decision policy:
        # If any trigger matched -> Route to backend for hybrid verification
        # If no trigger matched -> Retain on device as "Likely Safe"
        should_route = len(triggers) > 0

        return {
            "should_route_to_backend": should_route,
            "local_risk_tier": "Candidate" if should_route else "Likely Safe",
            "triggers_detected": triggers,
            "reason": "Triggers detected; server verification required" if should_route else "No threat signals detected; filtered on device",
            "savings_category": "ROUTED_CANDIDATE" if should_route else "FILTERED_BENIGN_LOCAL",
        }


# Singleton instance
default_local_prefilter = LocalPrefilter()
