"""
Feedback Router
Handles farmer feedback submissions.
"""
import logging

from fastapi import APIRouter, HTTPException

from app.models import FeedbackRequest
from app.services.supabase_client import store_feedback

logger = logging.getLogger("c-dit")

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("")
async def submit_feedback(body: FeedbackRequest):
    """POST /feedback — submit farmer feedback for a session."""
    if not body.sessionId or len(body.sessionId.strip()) == 0:
        raise HTTPException(status_code=400, detail="Session ID is required.")
    if body.rating < 1 or body.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

    logger.info(f"Feedback submission (session={body.sessionId}, rating={body.rating})")

    store_feedback(body.model_dump())

    return {
        "success": True,
        "message": "Thank you for your feedback! It helps us improve our advisory system.",
    }
