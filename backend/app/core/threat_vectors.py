"""
Decomposed Threat Vector Scoring Engine.
Calculates multidimensional risk ratings (0-100) across six independent threat vectors.
"""
from typing import Dict, Any
from backend.app.core.rules import default_rule_engine
from backend.app.core.url_intel import default_url_intel


class ThreatVectorEngine:
    """Decomposes holistic risk into 6 explainable security dimensions."""

    def compute_vectors(self, text: str, ml_probability: float = 0.0) -> Dict[str, Any]:
        if not text or not text.strip():
            return self._empty_vectors()

        rule_eval = default_rule_engine.evaluate(text)
        url_eval = default_url_intel.analyze(text)

        matched_cats = {ind["category"]: ind for ind in rule_eval.get("indicators", [])}

        # 1. Urgency & Coercion
        urgency_score = 0.0
        if "URGENCY_THREAT" in matched_cats:
            urgency_score = 75.0 if len(matched_cats["URGENCY_THREAT"].get("matched_snippets", [])) > 1 else 60.0

        # 2. Financial & Payment Risk
        fin_score = 0.0
        if "FINANCIAL_LURE" in matched_cats:
            fin_score += 65.0
        if "SUSPICIOUS_PAYMENT" in matched_cats:
            fin_score += 70.0
        fin_score = min(100.0, fin_score)

        # 3. Credential Harvesting (Critical)
        cred_score = 0.0
        if "CREDENTIAL_HARVEST" in matched_cats:
            cred_score = 95.0
        # Inspect URL path tokens for credential harvesting endpoints
        for detail in url_eval.get("details", []):
            raw = detail.get("raw_url", "").lower()
            if any(path in raw for path in ["/login", "/verify", "/signin", "/auth", "/update", "/portal", "/account"]):
                cred_score = max(cred_score, 75.0)

        # 4. Impersonation (Authority / Institution)
        imp_score = 0.0
        if "IMPERSONATION" in matched_cats:
            imp_score = 65.0
        # If domain analysis caught typosquatting, add to impersonation
        for detail in url_eval.get("details", []):
            if detail.get("typosquatting_detected"):
                imp_score = max(imp_score, 85.0)

        # 5. Link & Domain Risk
        link_score = float(url_eval.get("url_risk_score", 0.0))
        if "SUSPICIOUS_LINKS" in matched_cats:
            link_score = max(link_score, 70.0)

        # 6. Social Engineering & Call to Action
        se_score = 0.0
        if "CALL_BACK_LURE" in matched_cats:
            se_score += 55.0
        if ml_probability >= 0.70:
            se_score += 35.0
        elif ml_probability >= 0.40:
            se_score += 15.0
        se_score = min(100.0, se_score)

        vectors = {
            "urgency_coercion": round(urgency_score, 1),
            "financial_risk": round(fin_score, 1),
            "credential_harvesting": round(cred_score, 1),
            "impersonation": round(imp_score, 1),
            "link_domain_risk": round(link_score, 1),
            "social_engineering": round(se_score, 1),
        }

        # Vector ratings
        ratings = {}
        for k, v in vectors.items():
            ratings[k] = (
                "CRITICAL" if v >= 75.0 else
                "HIGH" if v >= 50.0 else
                "MODERATE" if v >= 25.0 else
                "CLEAN"
            )

        return {
            "scores": vectors,
            "ratings": ratings,
            "primary_vector": max(vectors, key=vectors.get),
            "url_intelligence": url_eval,
        }

    def _empty_vectors(self) -> Dict[str, Any]:
        zeros = {
            "urgency_coercion": 0.0,
            "financial_risk": 0.0,
            "credential_harvesting": 0.0,
            "impersonation": 0.0,
            "link_domain_risk": 0.0,
            "social_engineering": 0.0,
        }
        return {
            "scores": zeros,
            "ratings": {k: "CLEAN" for k in zeros},
            "primary_vector": "None",
            "url_intelligence": {"has_urls": False, "url_count": 0, "url_risk_score": 0.0, "details": [], "summary": "No URLs"}
        }


default_threat_vectors = ThreatVectorEngine()
