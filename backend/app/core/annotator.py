"""
Interactive Message Annotator and Threat Token Attribution.
Identifies and annotates specific tokens/spans in a message with threat categories and explanations.
"""
import re
from typing import List, Dict, Any
from backend.app.core.rules import default_rule_engine
from backend.app.core.url_intel import default_url_intel


class MessageAnnotator:
    """Extracts highlighted spans and token-level threat attribution for UI rendering."""

    def annotate(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "spans": [],
                "highlighted_html": text,
                "threat_word_count": 0
            }

        spans: List[Dict[str, Any]] = []

        # 1. URL Spans
        urls = default_url_intel.extract_urls(text)
        for u in urls:
            for match in re.finditer(re.escape(u), text):
                spans.append({
                    "start": match.start(),
                    "end": match.end(),
                    "token": match.group(),
                    "category": "SUSPICIOUS_LINK",
                    "severity": "HIGH",
                    "explanation": "Embedded link requiring domain authenticity inspection."
                })

        # 2. Heuristic Rule Matches
        rule_eval = default_rule_engine.evaluate(text)
        for ind in rule_eval.get("indicators", []):
            cat = ind["category"]
            sev = ind["severity"]
            desc = ind["description"]
            for snippet in ind.get("matched_snippets", []):
                if len(snippet) < 3:
                    continue
                # Find occurrences of snippet in text
                try:
                    for match in re.finditer(r"\b" + re.escape(snippet) + r"\b", text, re.IGNORECASE):
                        spans.append({
                            "start": match.start(),
                            "end": match.end(),
                            "token": match.group(),
                            "category": cat,
                            "severity": sev,
                            "explanation": desc
                        })
                except re.error:
                    pass

        # 3. Masked PII Spans
        pii_tokens = ["[PHONE_REDACTED]", "[CARD_NUMBER_REDACTED]", "[ID_NUMBER_REDACTED]"]
        for pii in pii_tokens:
            for match in re.finditer(re.escape(pii), text):
                spans.append({
                    "start": match.start(),
                    "end": match.end(),
                    "token": match.group(),
                    "category": "PII_MASKED",
                    "severity": "LOW",
                    "explanation": "Sensitive user identity token pseudonymized locally."
                })

        # Sort and deduplicate overlapping spans
        spans = sorted(spans, key=lambda s: (s["start"], -(s["end"] - s["start"])))
        non_overlapping: List[Dict[str, Any]] = []
        last_end = 0

        for s in spans:
            if s["start"] >= last_end:
                non_overlapping.append(s)
                last_end = s["end"]

        # Build clean highlighted HTML markup
        html_parts = []
        curr_idx = 0

        severity_color_classes = {
            "CRITICAL": "bg-rose-500/25 border-rose-500/60 text-rose-300 font-semibold",
            "HIGH": "bg-amber-500/25 border-amber-500/60 text-amber-300 font-semibold",
            "MEDIUM": "bg-yellow-500/20 border-yellow-500/50 text-yellow-300",
            "LOW": "bg-indigo-500/20 border-indigo-500/40 text-indigo-300",
        }

        for s in non_overlapping:
            if s["start"] > curr_idx:
                html_parts.append(text[curr_idx:s["start"]])
            token_text = text[s["start"]:s["end"]]
            color_class = severity_color_classes.get(s["severity"], "bg-slate-700/50 text-slate-200")
            span_html = (
                f'<span class="threat-token px-1.5 py-0.5 rounded border {color_class} cursor-help transition-all" '
                f'title="[{s["severity"]}] {s["category"]}: {s["explanation"]}">{token_text}</span>'
            )
            html_parts.append(span_html)
            curr_idx = s["end"]

        if curr_idx < len(text):
            html_parts.append(text[curr_idx:])

        return {
            "spans": non_overlapping,
            "highlighted_html": "".join(html_parts),
            "threat_word_count": len(non_overlapping)
        }


default_message_annotator = MessageAnnotator()
