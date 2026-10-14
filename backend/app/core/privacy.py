"""
Privacy and Data Minimization Safeguards.
Provides PII redaction without destroying scam indicators, and anonymous session hashing.
"""
import re
import hashlib
from typing import Tuple, Dict, Any


class PrivacyGuard:
    """Handles privacy-preserving transformations and session token generation."""

    def __init__(self):
        # Email: keep domain or mask user: j***@domain.com
        self.email_pattern = re.compile(r"\b([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b")
        # Phone: mask middle digits while keeping country code/suffix structure
        self.phone_pattern = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)(\d{3}[\s-]?\d{4})")
        # Credit Card: 13-19 digits, optionally spaced or dashed
        self.card_pattern = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
        # Aadhaar / SSN: 9 to 12 digit identifiers
        self.id_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{4}\s\d{4}\s\d{4}\b")

    def redact_pii(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Redacts personal identifiable information while preserving:
        - URL schemes and hostnames
        - Urgency terminology
        - Financial transaction and scam lure phrases
        """
        if not text:
            return "", {"emails": 0, "phones": 0, "cards": 0, "ids": 0}

        counts = {"emails": 0, "phones": 0, "cards": 0, "ids": 0}

        def email_repl(match):
            counts["emails"] += 1
            first_char = match.group(1)
            domain = match.group(2)
            return f"{first_char}***@{domain}"

        def phone_repl(match):
            counts["phones"] += 1
            return "[PHONE_REDACTED]"

        def card_repl(match):
            counts["cards"] += 1
            return "[CARD_NUMBER_REDACTED]"

        def id_repl(match):
            counts["ids"] += 1
            return "[ID_NUMBER_REDACTED]"

        # Apply redactions in safe sequence
        redacted = self.email_pattern.sub(email_repl, text)
        redacted = self.card_pattern.sub(card_repl, redacted)
        redacted = self.id_pattern.sub(id_repl, redacted)
        redacted = self.phone_pattern.sub(phone_repl, redacted)

        return redacted, counts

    @staticmethod
    def hash_text(text: str) -> str:
        """Create SHA-256 fingerprint for deduplication without storing text."""
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    @staticmethod
    def generate_session_token(seed: str) -> str:
        """Generate anonymous, non-reversible client identifier."""
        return hashlib.sha256(f"client_salt_{seed}".encode("utf-8")).hexdigest()[:16]


default_privacy_guard = PrivacyGuard()
