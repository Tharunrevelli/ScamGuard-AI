"""
URL & Domain Threat Intelligence Engine.
Analyzes embedded URLs, domain entropy, typosquatting/homographs, and TLD reputation.
"""
import re
import math
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse


KNOWN_TARGET_BRANDS = [
    "paypal", "amazon", "netflix", "apple", "google", "microsoft",
    "chase", "wellsfargo", "bankofamerica", "citibank", "binance",
    "coinbase", "fedex", "dhl", "ups", "usps", "metamask", "telegram",
    "whatsapp", "instagram", "facebook", "geeksquad", "mcafee", "norton"
]

RISKY_TLDS = {
    "xyz", "top", "club", "work", "buzz", "icu", "live", "monster",
    "cam", "link", "stream", "gq", "cf", "tk", "ml", "ga", "click",
    "shop", "site", "online", "vip", "bid", "loan", "men", "party"
}

KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy",
    "shorturl.at", "ow.ly", "buff.ly", "goo.gl", "bit.do", "rebrand.ly"
}


def compute_shannon_entropy(string: str) -> float:
    """Calculates Shannon entropy of a string (higher entropy indicates randomized DGA domain)."""
    if not string:
        return 0.0
    probabilities = [float(string.count(c)) / len(string) for c in set(string)]
    return -sum(p * math.log2(p) for p in probabilities)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class URLThreatIntelligence:
    """Performs deep forensic inspection of URLs and domain names embedded in text."""

    def __init__(self):
        # Comprehensive URL extraction pattern
        self.url_regex = re.compile(
            r"(?:https?://|www\.)[^\s/$.?#].[^\s]*|"
            r"\b[a-zA-Z0-9-]+\.(?:com|org|net|info|biz|xyz|top|club|ru|cn|in|uk|io|me|cc|co|vip|app|dev)/[^\s]*",
            re.IGNORECASE
        )
        self.ip_url_regex = re.compile(
            r"https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?",
            re.IGNORECASE
        )

    def extract_urls(self, text: str) -> List[str]:
        if not text:
            return []
        found = self.url_regex.findall(text)
        ip_found = self.ip_url_regex.findall(text)
        # Normalize URLs
        all_urls = list(set(found + ip_found))
        clean_urls = []
        for u in all_urls:
            # Strip trailing punctuation often caught in sentences
            u_clean = u.rstrip(".,;:!?)'\"")
            if u_clean:
                clean_urls.append(u_clean)
        return clean_urls

    def analyze(self, text: str) -> Dict[str, Any]:
        urls = self.extract_urls(text)
        if not urls:
            return {
                "has_urls": False,
                "url_count": 0,
                "url_risk_score": 0.0,
                "details": [],
                "summary": "No hyperlinks or domains detected."
            }

        details = []
        max_url_risk = 0.0

        for url in urls:
            parsed = self._inspect_url(url)
            details.append(parsed)
            if parsed["risk_score"] > max_url_risk:
                max_url_risk = parsed["risk_score"]

        # Aggregate summary
        flagged_count = sum(1 for d in details if d["risk_score"] >= 40)
        summary = (
            f"Detected {len(urls)} URL(s), {flagged_count} displaying deceptive, obfuscated, or untrusted attributes."
            if flagged_count > 0 else
            f"Detected {len(urls)} URL(s) with standard structural parameters."
        )

        return {
            "has_urls": True,
            "url_count": len(urls),
            "url_risk_score": round(max_url_risk, 1),
            "details": details,
            "summary": summary
        }

    def _inspect_url(self, raw_url: str) -> Dict[str, Any]:
        # Ensure scheme for urllib parsing
        full_url = raw_url if raw_url.startswith(("http://", "https://")) else f"http://{raw_url}"
        parsed = urlparse(full_url)
        hostname = (parsed.hostname or "").lower()

        is_ip = bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", hostname))
        is_shortener = hostname in KNOWN_SHORTENERS
        parts = hostname.split(".")
        tld = parts[-1] if len(parts) > 1 else ""
        is_risky_tld = tld in RISKY_TLDS

        # Shannon entropy of primary domain name
        domain_sld = parts[-2] if len(parts) >= 2 else hostname
        entropy = compute_shannon_entropy(domain_sld)
        high_entropy = entropy > 3.8 and len(domain_sld) > 9

        # Typosquatting / Brand Spoofing Check
        spoofed_brand: Optional[str] = None
        typosquatting_detected = False

        # Check direct substring matching (e.g., "chase-security-verify", "bofa-verify")
        for brand in KNOWN_TARGET_BRANDS:
            if brand in hostname:
                # Is it an official domain (e.g. chase.com, amazon.com)?
                if not (hostname == f"{brand}.com" or hostname.endswith(f".{brand}.com")):
                    spoofed_brand = brand
                    typosquatting_detected = True
                    break
            else:
                # Check Levenshtein distance on SLD parts (e.g., "paypa1" vs "paypal")
                for subpart in re.split(r"[-_.]", domain_sld):
                    if len(subpart) >= 4 and abs(len(subpart) - len(brand)) <= 1:
                        dist = levenshtein_distance(subpart, brand)
                        if dist == 1 or (dist == 2 and len(brand) >= 7):
                            spoofed_brand = brand
                            typosquatting_detected = True
                            break
            if typosquatting_detected:
                break

        # Compute numerical risk score for this individual URL
        risk_score = 0.0
        risk_factors = []

        if is_ip:
            risk_score += 75.0
            risk_factors.append("Direct IP address used instead of domain name (bypasses DNS verification).")

        if typosquatting_detected and spoofed_brand:
            risk_score += 65.0
            risk_factors.append(f"Domain impersonates known brand '{spoofed_brand}' on unauthorized infrastructure.")

        if is_risky_tld:
            risk_score += 35.0
            risk_factors.append(f"High-abuse top-level domain '.{tld}' commonly associated with throwaway smishing campaigns.")

        if is_shortener:
            risk_score += 30.0
            risk_factors.append(f"Shortened redirect link ({hostname}) masks final destination domain.")

        if high_entropy:
            risk_score += 25.0
            risk_factors.append(f"High-entropy randomized domain label (Shannon Entropy: {entropy:.2f}).")

        # Subdomain nesting check (e.g., login.chase.com.evil-domain.xyz)
        if len(parts) > 3 and not is_ip:
            risk_score += 20.0
            risk_factors.append("Excessive subdomain nesting often used to conceal real registrant identity.")

        risk_score = min(100.0, max(0.0, risk_score))

        severity = (
            "CRITICAL" if risk_score >= 70.0 else
            "HIGH" if risk_score >= 45.0 else
            "MEDIUM" if risk_score >= 20.0 else
            "LOW"
        )

        return {
            "raw_url": raw_url,
            "hostname": hostname,
            "tld": tld,
            "is_ip": is_ip,
            "is_shortener": is_shortener,
            "is_risky_tld": is_risky_tld,
            "typosquatting_detected": typosquatting_detected,
            "spoofed_brand": spoofed_brand,
            "entropy": round(entropy, 2),
            "risk_score": round(risk_score, 1),
            "severity": severity,
            "risk_factors": risk_factors
        }


# Global singleton instance
default_url_intel = URLThreatIntelligence()
