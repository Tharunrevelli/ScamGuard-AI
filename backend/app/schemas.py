"""
Pydantic Data Schemas and Validation Models.
Strict contracts for requests, detection results, history, feedback, and model metadata.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


MessageSource = Literal["MANUAL", "NOTIFICATION", "SHARE_SHEET", "CLIPBOARD", "BENCHMARK", "SMS", "SMS_BROADCAST", "GMAIL_API", "WHATSAPP_COMPANION"]
ClassificationTier = Literal["Likely Safe", "Suspicious", "Likely Scam", "Unable to Determine"]


class DetectionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000, description="Message body or preview text to inspect")
    source: MessageSource = Field(default="MANUAL", description="Origin of the inspected message event")
    sender: Optional[str] = Field(default=None, description="Sender name, phone, or email address")
    is_sender_in_contacts: bool = Field(default=False, description="Whether the sender is verified in the user's local contact address book")
    package_name: Optional[str] = Field(default=None, description="Android package name of the originating app")
    client_session_id: Optional[str] = Field(default=None, description="Optional client identifier for session isolation")
    bypass_prefilter: bool = Field(default=False, description="Whether to bypass Stage 1 local filtering")
    redact_pii_before_analysis: bool = Field(default=False, description="Enable client/edge PII sanitization")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message text cannot be purely whitespace.")
        return trimmed


class RiskIndicator(BaseModel):
    category: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    description: str
    matched_snippets: List[str] = []


class ScoreBreakdown(BaseModel):
    ml_probability: float = Field(..., ge=0.0, le=1.0)
    ml_risk_score: float = Field(..., ge=0.0, le=100.0)
    rule_risk_score: float = Field(..., ge=0.0, le=100.0)
    matched_rule_count: int = Field(..., ge=0)
    has_critical_indicators: bool


class DetectionResponse(BaseModel):
    request_id: str
    classification: ClassificationTier
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Calibrated risk index from 0 to 100")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence certainty factor")
    reasons: List[str]
    suggested_actions: List[str]
    indicators: List[RiskIndicator] = []
    breakdown: Optional[Dict[str, Any]] = None
    model_version: str
    processing_time_ms: float
    stage_applied: str
    pii_redacted: bool = False
    redacted_preview: Optional[str] = None
    threat_vectors: Optional[Dict[str, Any]] = None
    url_intelligence: Optional[Dict[str, Any]] = None
    annotated_message: Optional[Dict[str, Any]] = None
    token_attributions: Optional[List[Dict[str, Any]]] = None
    is_truncated: bool = False
    truncation_warning: Optional[str] = None


class PrefilterCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    user_requested: bool = False
    in_contacts: bool = False
    package_name: Optional[str] = None


class PrefilterCheckResponse(BaseModel):
    should_route_to_backend: bool
    local_risk_tier: str
    triggers_detected: List[str]
    reason: str
    savings_category: str


class BatchEvaluateRequest(BaseModel):
    messages: List[str] = Field(..., min_length=1, max_length=200)
    use_prefilter: bool = True


class BatchEvaluateItem(BaseModel):
    text_snippet: str
    prefilter_routed: bool
    classification: str
    risk_score: float
    processing_time_ms: float


class BatchEvaluateResponse(BaseModel):
    total_messages: int
    routed_to_backend: int
    filtered_locally: int
    request_reduction_pct: float
    results: List[BatchEvaluateItem]


class BatchDetectRequest(BaseModel):
    messages: List[str] = Field(..., min_length=1, max_length=500, description="List of concurrent notification message texts to evaluate")
    source: MessageSource = Field(default="NOTIFICATION", description="Source of notifications")
    app_packages: Optional[List[str]] = Field(default=None, description="Optional package names corresponding to each notification")


class BatchDetectItemResult(BaseModel):
    index: int
    text_snippet: str
    package_name: Optional[str] = None
    classification: ClassificationTier
    risk_score: float
    confidence: float
    is_truncated: bool = False
    truncation_warning: Optional[str] = None
    processing_time_ms: float


class BatchDetectResponse(BaseModel):
    total_processed: int
    total_latency_ms: float
    avg_latency_ms: float
    results: List[BatchDetectItemResult]
    throughput_items_per_sec: float


class FeedbackRequest(BaseModel):
    request_id: str
    actual_label: Literal["scam", "safe", "ambiguous"]
    user_notes: Optional[str] = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    status: str
    message: str


class HistoryItem(BaseModel):
    id: int
    request_id: str
    timestamp: str
    source: str
    classification: str
    risk_score: float
    latency_ms: float


class HistoryResponse(BaseModel):
    total_count: int
    items: List[HistoryItem]


class ModelInfoResponse(BaseModel):
    model_version: str
    architecture: str
    is_loaded: bool
    training_dataset: str
    dataset_provenance: str
    metrics: Dict[str, Any]
    top_features: Dict[str, Any]
