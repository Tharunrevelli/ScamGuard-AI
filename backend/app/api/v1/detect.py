"""
Detection Endpoints: /detect, /prefilter-check, and /evaluate-batch.
"""
import time
import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from backend.app.schemas import (
    DetectionRequest,
    DetectionResponse,
    PrefilterCheckRequest,
    PrefilterCheckResponse,
    BatchEvaluateRequest,
    BatchEvaluateResponse,
    BatchEvaluateItem,
    BatchDetectRequest,
    BatchDetectResponse,
    BatchDetectItemResult,
    RiskIndicator,
)
from backend.app.core.rules import default_rule_engine
from backend.app.core.prefilter import default_local_prefilter
from backend.app.core.hybrid import default_hybrid_engine
from backend.app.core.privacy import default_privacy_guard
from backend.app.core.rate_limiter import default_rate_limiter
from backend.app.ml.model import default_model_service
from backend.app.db.database import default_db_manager

router = APIRouter()


@router.post(
    "/detect",
    response_model=DetectionResponse,
    summary="Detect Scam Indicators in Message Text",
    description="Processes text through the hybrid rule + ML engine and returns calibrated risk assessment."
)
async def detect_message(payload: DetectionRequest, request: Request):
    # Enforce rate limiting
    default_rate_limiter.check_request(request)

    t0 = time.perf_counter()
    request_id = str(uuid.uuid4())
    client_seed = payload.client_session_id or request.client.host if request.client else "default_session"
    session_hash = default_privacy_guard.generate_session_token(client_seed)

    raw_text = payload.text
    processed_text = raw_text
    redacted_preview = None
    pii_redacted = False

    # Optional PII Redaction
    if payload.redact_pii_before_analysis:
        processed_text, redaction_counts = default_privacy_guard.redact_pii(raw_text)
        pii_redacted = sum(redaction_counts.values()) > 0
        if pii_redacted:
            redacted_preview = processed_text[:120] + ("..." if len(processed_text) > 120 else "")

    # Stage 1: Optional Local Prefilter check simulation if event came from background notification,
    # SMS broadcast, Gmail API, or WhatsApp companion, and bypass_prefilter is False
    stage_applied = "HYBRID_REMOTE"
    background_sources = ("NOTIFICATION", "SMS_BROADCAST", "GMAIL_API", "WHATSAPP_COMPANION")
    if not payload.bypass_prefilter and payload.source in background_sources:
        pre_check = default_local_prefilter.evaluate(
            processed_text,
            user_requested=False,
            in_contacts=payload.is_sender_in_contacts,
            package_name=payload.package_name
        )
        if not pre_check["should_route_to_backend"]:
            # Edge filter satisfied: Classified as Likely Safe on device
            elapsed_ms = (time.perf_counter() - t0) * 1000
            default_db_manager.record_detection(
                request_id=request_id,
                session_hash=session_hash,
                source=payload.source,
                classification="Likely Safe",
                risk_score=5.0,
                model_version="stage1-edge-filter",
                latency_ms=round(elapsed_ms, 2)
            )
            reasons = [
                f"Stage 1 on-device filter: {pre_check['reason']}",
                "No URLs, monetary lures, urgent threats, or credential requests detected."
            ]
            return DetectionResponse(
                request_id=request_id,
                classification="Likely Safe",
                risk_score=5.0,
                confidence=0.95 if pre_check["savings_category"] == "FILTERED_VERIFIED_CONTACT" else 0.92,
                reasons=reasons,
                suggested_actions=["Standard vigilance advised."],
                indicators=[],
                breakdown={
                    "ml_risk": 0.0,
                    "rule_risk": 0.0,
                    "stage1_filtered": True,
                    "savings_category": pre_check["savings_category"]
                },
                model_version="stage1-edge-prefilter",
                processing_time_ms=round(elapsed_ms, 2),
                stage_applied="STAGE_1_LOCAL_FILTER",
                pii_redacted=pii_redacted,
                redacted_preview=redacted_preview,
            )

    # Stage 2: Full Hybrid Inference
    rule_result = default_rule_engine.evaluate(processed_text)
    ml_result = default_model_service.predict(processed_text)
    hybrid_result = default_hybrid_engine.evaluate(processed_text, rule_result, ml_result)

    elapsed_ms = (time.perf_counter() - t0) * 1000

    # Format indicators
    indicators_formatted = [
        RiskIndicator(
            category=ind["category"],
            severity=ind["severity"],
            description=ind["description"],
            matched_snippets=ind["matched_snippets"]
        ) for ind in rule_result.get("indicators", [])
    ]

    # Privacy-conscious metadata logging (zero raw text stored)
    default_db_manager.record_detection(
        request_id=request_id,
        session_hash=session_hash,
        source=payload.source,
        classification=hybrid_result["classification"],
        risk_score=hybrid_result["risk_score"],
        model_version=ml_result["model_version"],
        latency_ms=round(elapsed_ms, 2)
    )

    # Truncation check
    is_truncated, truncation_warning = default_local_prefilter.check_truncation(processed_text)
    reasons_list = list(hybrid_result["reasons"])
    actions_list = list(hybrid_result["suggested_actions"])

    if is_truncated:
        reasons_list.append("Notice: Notification or input text appears truncated. Ensure full message is submitted via Share Sheet or Manual Paste for exhaustive confidence.")
        actions_list.insert(0, "Verify full unclipped message via Share Sheet or Manual Paste.")

    return DetectionResponse(
        request_id=request_id,
        classification=hybrid_result["classification"],
        risk_score=hybrid_result["risk_score"],
        confidence=hybrid_result["confidence"],
        reasons=reasons_list,
        suggested_actions=actions_list,
        indicators=indicators_formatted,
        breakdown=hybrid_result["breakdown"],
        model_version=ml_result["model_version"],
        processing_time_ms=round(elapsed_ms, 2),
        stage_applied=stage_applied,
        pii_redacted=pii_redacted,
        redacted_preview=redacted_preview,
        threat_vectors=hybrid_result.get("threat_vectors"),
        url_intelligence=hybrid_result.get("url_intelligence"),
        annotated_message=hybrid_result.get("annotated_message"),
        token_attributions=hybrid_result.get("token_attributions"),
        is_truncated=is_truncated,
        truncation_warning=truncation_warning,
    )


@router.post(
    "/prefilter-check",
    response_model=PrefilterCheckResponse,
    summary="Simulate Stage 1 On-Device Prefilter",
    description="Tests the lightweight local prefilter logic to determine if a message warrants backend transmission."
)
async def check_prefilter(payload: PrefilterCheckRequest):
    res = default_local_prefilter.evaluate(
        payload.text,
        user_requested=payload.user_requested,
        in_contacts=payload.in_contacts,
        package_name=payload.package_name
    )
    return PrefilterCheckResponse(
        should_route_to_backend=res["should_route_to_backend"],
        local_risk_tier=res["local_risk_tier"],
        triggers_detected=res["triggers_detected"],
        reason=res["reason"],
        savings_category=res["savings_category"]
    )


@router.post(
    "/evaluate-batch",
    response_model=BatchEvaluateResponse,
    summary="Batch Evaluation for Experimental Testing",
    description="Evaluates multiple sample messages and measures backend request reduction and classification results."
)
async def evaluate_batch(payload: BatchEvaluateRequest):
    total = len(payload.messages)
    routed_count = 0
    filtered_count = 0
    items: List[BatchEvaluateItem] = []

    for msg in payload.messages:
        t0 = time.perf_counter()
        if payload.use_prefilter:
            pre_res = default_local_prefilter.evaluate(msg, user_requested=False)
            if not pre_res["should_route_to_backend"]:
                filtered_count += 1
                items.append(BatchEvaluateItem(
                    text_snippet=msg[:50] + ("..." if len(msg) > 50 else ""),
                    prefilter_routed=False,
                    classification="Likely Safe (Edge)",
                    risk_score=5.0,
                    processing_time_ms=round((time.perf_counter() - t0) * 1000, 2)
                ))
                continue

        routed_count += 1
        r_res = default_rule_engine.evaluate(msg)
        m_res = default_model_service.predict(msg)
        h_res = default_hybrid_engine.evaluate(msg, r_res, m_res)
        items.append(BatchEvaluateItem(
            text_snippet=msg[:50] + ("..." if len(msg) > 50 else ""),
            prefilter_routed=True,
            classification=h_res["classification"],
            risk_score=h_res["risk_score"],
            processing_time_ms=round((time.perf_counter() - t0) * 1000, 2)
        ))

    reduction_pct = round((filtered_count / total) * 100.0, 2) if total > 0 else 0.0

    return BatchEvaluateResponse(
        total_messages=total,
        routed_to_backend=routed_count,
        filtered_locally=filtered_count,
        request_reduction_pct=reduction_pct,
        results=items
    )


@router.post(
    "/detect/batch",
    response_model=BatchDetectResponse,
    summary="High-Concurrency Batch Notification Detector",
    description="Vectorized batch processing for 100+ concurrent notifications from multiple apps. Demonstrates backend scalability under notification floods."
)
async def detect_batch_messages(payload: BatchDetectRequest):
    t0 = time.perf_counter()
    messages = payload.messages
    total = len(messages)
    packages = payload.app_packages or []

    # 1. Vectorized ML Inference pass across all messages at once
    ml_results = default_model_service.predict_batch(messages)

    results: List[BatchDetectItemResult] = []
    for i, msg in enumerate(messages):
        t_item_0 = time.perf_counter()
        pkg = packages[i] if i < len(packages) else None

        # Check truncation
        is_trunc, trunc_warn = default_local_prefilter.check_truncation(msg)

        # Rule evaluation
        r_res = default_rule_engine.evaluate(msg)
        m_res = ml_results[i]
        h_res = default_hybrid_engine.evaluate(msg, r_res, m_res)
        item_ms = (time.perf_counter() - t_item_0) * 1000

        results.append(BatchDetectItemResult(
            index=i,
            text_snippet=msg[:60] + ("..." if len(msg) > 60 else ""),
            package_name=pkg,
            classification=h_res["classification"],
            risk_score=h_res["risk_score"],
            confidence=h_res["confidence"],
            is_truncated=is_trunc,
            truncation_warning=trunc_warn,
            processing_time_ms=round(item_ms, 2)
        ))

    total_latency_ms = (time.perf_counter() - t0) * 1000
    avg_latency = total_latency_ms / total if total > 0 else 0.0
    throughput = (total / (total_latency_ms / 1000.0)) if total_latency_ms > 0 else 0.0

    return BatchDetectResponse(
        total_processed=total,
        total_latency_ms=round(total_latency_ms, 2),
        avg_latency_ms=round(avg_latency, 3),
        results=results,
        throughput_items_per_sec=round(throughput, 1)
    )


@router.post(
    "/report",
    summary="Generate Forensic Threat Incident Report",
    description="Generates an in-depth digital forensic investigation report with IOCs, threat vectors, and playbook actions."
)
async def generate_report(payload: DetectionRequest):
    t0 = time.perf_counter()
    raw_text = payload.text
    rule_res = default_rule_engine.evaluate(raw_text)
    ml_res = default_model_service.predict(raw_text)
    hybrid_res = default_hybrid_engine.evaluate(raw_text, rule_res, ml_res)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    report_id = f"SG-FR-{uuid.uuid4().hex[:8].upper()}"
    sha256_hash = default_privacy_guard.hash_text(raw_text)

    # Format IOCs (Indicators of Compromise)
    iocs = []
    for u in hybrid_res.get("url_intelligence", {}).get("details", []):
        iocs.append({
            "type": "URL/DOMAIN",
            "value": u["raw_url"],
            "risk_score": u["risk_score"],
            "notes": "; ".join(u.get("risk_factors", [])) or "Standard URL"
        })

    for ind in rule_res.get("indicators", []):
        for snip in ind.get("matched_snippets", []):
            iocs.append({
                "type": f"REGEX_PATTERN/{ind['category']}",
                "value": snip,
                "risk_score": 75.0 if ind["severity"] in ("CRITICAL", "HIGH") else 40.0,
                "notes": ind["description"]
            })

    return {
        "report_id": report_id,
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "message_hash_sha256": sha256_hash,
        "classification": hybrid_res["classification"],
        "risk_score": hybrid_res["risk_score"],
        "confidence_level": f"{hybrid_res['confidence']*100:.1f}%",
        "primary_threat_vector": hybrid_res.get("threat_vectors", {}).get("primary_vector", "None"),
        "threat_vectors": hybrid_res.get("threat_vectors", {}).get("scores", {}),
        "threat_ratings": hybrid_res.get("threat_vectors", {}).get("ratings", {}),
        "indicators_of_compromise": iocs,
        "forensic_reasons": hybrid_res["reasons"],
        "incident_playbook_actions": hybrid_res["suggested_actions"],
        "model_architecture": ml_res["model_version"],
        "investigation_latency_ms": round(elapsed_ms, 2),
    }
