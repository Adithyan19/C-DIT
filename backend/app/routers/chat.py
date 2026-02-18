"""
Chat Router
Handles follow-up questions within an existing conversation session.
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models import ChatFollowupRequest, ChatMessage
from app.services.embedding import generate_embedding
from app.services.vector_index import search_similar
from app.services.prompt_builder import build_followup_prompt
from app.services.sample_model import generate_followup_response
from app.services.supabase_client import store_message, get_session_messages

logger = logging.getLogger("c-dit")

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/followup")
async def followup(body: ChatFollowupRequest):
    """POST /chat/followup — follow-up question with session context."""
    if not body.sessionId or len(body.sessionId.strip()) == 0:
        raise HTTPException(status_code=400, detail="Session ID is required.")
    if not body.message or len(body.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message is required.")

    session_id = body.sessionId.strip()
    message = body.message.strip()

    logger.info(f"Follow-up request (session={session_id}, length={len(message)})")

    # Get conversation history from Supabase
    raw_messages = get_session_messages(session_id)
    history = [
        ChatMessage(
            role=m.get("role", "farmer"),
            content=m.get("content", ""),
            timestamp=m.get("timestamp", ""),
        )
        for m in raw_messages
    ]

    # Retrieve additional context
    query_embedding = await generate_embedding(message)
    contexts = search_similar(query_embedding, 3)

    # Build prompt and generate response
    prompt = build_followup_prompt(message, history, contexts)
    reply = await generate_followup_response(prompt)

    # Store messages in Supabase
    now = datetime.now(timezone.utc).isoformat()
    store_message(session_id, "farmer", message, now)
    store_message(session_id, "assistant", reply, now)

    return {
        "success": True,
        "data": {
            "sessionId": session_id,
            "reply": reply,
            "timestamp": now,
        },
    }
