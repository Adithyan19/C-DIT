"""
Supabase client implementation using postgrest-py.
Lightweight alternative to the full supabase-js/py to avoid heavy dependencies.
"""
import logging
from typing import Optional, List, Dict, Any

from postgrest import SyncPostgrestClient
from app.config import settings

logger = logging.getLogger("c-dit")

_client: Optional[SyncPostgrestClient] = None

def get_supabase() -> SyncPostgrestClient:
    """Get or create the PostgREST client singleton."""
    global _client
    if _client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        # PostgREST URL is the Supabase URL + /rest/v1
        base_url = f"{settings.supabase_url.rstrip('/')}/rest/v1"
        headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}"
        }
        _client = SyncPostgrestClient(base_url, headers=headers)
        logger.info("PostgREST client initialized")
    return _client

# ─── Session Helpers ─────────────────────────────────────────────────────────

def store_session(session_id: str, input_type: str) -> None:
    """Create a new session record."""
    try:
        get_supabase().table("sessions").upsert({
            "id": session_id,
            "input_type": input_type,
        }).execute()
    except Exception as e:
        logger.error(f"Failed to store session: {e}")

def store_message(session_id: str, role: str, content: str, timestamp: str) -> None:
    """Store a conversation message."""
    try:
        get_supabase().table("messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": timestamp,
        }).execute()
    except Exception as e:
        logger.error(f"Failed to store message: {e}")

def store_analysis_result(session_id: str, result: Dict[str, Any]) -> None:
    """Store an analysis result."""
    try:
        get_supabase().table("analysis_results").insert({
            "session_id": session_id,
            "disease_label": result.get("disease", {}).get("label", "Unknown"),
            "confidence": result.get("disease", {}).get("confidence", 0),
            "advisory": result.get("advisory", ""),
        }).execute()
    except Exception as e:
        logger.error(f"Failed to store analysis result: {e}")

def store_feedback(feedback: Dict[str, Any]) -> None:
    """Store farmer feedback."""
    try:
        get_supabase().table("feedback").insert({
            "session_id": feedback["sessionId"],
            "rating": feedback["rating"],
            "comment": feedback.get("comment"),
            "was_helpful": feedback["wasHelpful"],
            "correct_disease": feedback.get("correctDisease"),
        }).execute()
    except Exception as e:
        logger.error(f"Failed to store feedback: {e}")

def get_sessions(limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch recent sessions."""
    try:
        response = (
            get_supabase()
            .table("sessions")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception as e:
        logger.error(f"Failed to fetch sessions: {e}")
        return []

def get_session_messages(session_id: str) -> List[Dict[str, Any]]:
    """Fetch messages for a session."""
    try:
        response = (
            get_supabase()
            .table("messages")
            .select("*")
            .eq("session_id", session_id)
            .order("timestamp", desc=False)
            .execute()
        )
        return response.data or []
    except Exception as e:
        logger.error(f"Failed to fetch messages: {e}")
        return []

