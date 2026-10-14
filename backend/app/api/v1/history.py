"""
History Management Endpoints with Session Isolation.
Allows users to retrieve and delete their local audit records without cross-user leakage.
"""
from typing import Optional
from fastapi import APIRouter, Header, Request, HTTPException
from backend.app.schemas import HistoryResponse, HistoryItem
from backend.app.core.privacy import default_privacy_guard
from backend.app.db.database import default_db_manager

router = APIRouter()


def get_session_hash(request: Request, x_session_id: Optional[str] = Header(None)) -> str:
    seed = x_session_id or (request.client.host if request.client else "default_session")
    return default_privacy_guard.generate_session_token(seed)


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Get Privacy-Isolated Detection History",
    description="Retrieves metadata-only detection history for the current client session."
)
async def get_history(request: Request, x_session_id: Optional[str] = Header(None)):
    session_hash = get_session_hash(request, x_session_id)
    records = default_db_manager.get_history_by_session(session_hash)
    items = [
        HistoryItem(
            id=r["id"],
            request_id=r["request_id"],
            timestamp=r["timestamp"],
            source=r["source"],
            classification=r["classification"],
            risk_score=r["risk_score"],
            latency_ms=r["latency_ms"]
        ) for r in records
    ]
    return HistoryResponse(total_count=len(items), items=items)


@router.delete(
    "/history",
    summary="Delete Detection History for Session",
    description="Permanently deletes all audit metadata associated with the client session."
)
async def clear_history(request: Request, x_session_id: Optional[str] = Header(None)):
    session_hash = get_session_hash(request, x_session_id)
    deleted_count = default_db_manager.delete_history_by_session(session_hash)
    return {
        "status": "success",
        "deleted_count": deleted_count,
        "message": f"Successfully deleted {deleted_count} detection audit records."
    }
