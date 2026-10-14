"""
User Feedback Submission Endpoint.
Allows users to report false positives, false negatives, or ambiguous detections for auditing.
"""
from typing import Optional
from fastapi import APIRouter, Header, Request, HTTPException
from backend.app.schemas import FeedbackRequest, FeedbackResponse
from backend.app.core.privacy import default_privacy_guard
from backend.app.db.database import default_db_manager

router = APIRouter()


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit User Feedback on Detection Result",
    description="Records user corrections (e.g. false positive / false negative reports)."
)
async def submit_feedback(payload: FeedbackRequest, request: Request, x_session_id: Optional[str] = Header(None)):
    seed = x_session_id or (request.client.host if request.client else "default_session")
    session_hash = default_privacy_guard.generate_session_token(seed)

    ok = default_db_manager.record_feedback(
        request_id=payload.request_id,
        session_hash=session_hash,
        actual_label=payload.actual_label,
        user_notes=payload.user_notes
    )

    if not ok:
        raise HTTPException(status_code=500, detail="Failed to save user feedback.")

    return FeedbackResponse(
        status="success",
        message="Thank you for your feedback. This helps evaluate classifier performance."
    )
