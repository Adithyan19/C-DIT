"""
Analyze Router
Handles image, voice, and text analysis requests through the full RAG pipeline.
"""
import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.models import (
    AnalysisResult,
    ConfidenceLevel,
    DiseaseClassification,
    TextAnalysisRequest,
)
from app.services.sample_model import classify_image, speech_to_text, generate_advisory
from app.services.text_processing import process_text_input
from app.services.multimodal_fusion import fuse_inputs
from app.services.embedding import generate_embedding
from app.services.vector_index import search_similar
from app.services.prompt_builder import build_analysis_prompt
from app.services.supabase_client import store_session, store_message, store_analysis_result

logger = logging.getLogger("c-dit")

router = APIRouter(prefix="/analyze", tags=["analyze"])


async def _retrieve_context(query: str, top_k: int = 5):
    """Retrieve relevant context from the vector index."""
    query_embedding = await generate_embedding(query)
    return search_similar(query_embedding, top_k)


async def _run_analysis_pipeline(
    session_id: str,
    input_type: str,
    classification: Optional[DiseaseClassification],
    text_description: str,
) -> dict:
    """Full analysis pipeline: classify → fuse → embed → retrieve → prompt → LLM."""

    # 1. Fuse inputs
    fused = fuse_inputs(classification, text_description)

    # 2. Retrieve relevant context
    contexts = await _retrieve_context(fused.combinedQuery, 5)

    # 3. Build prompt
    prompt = build_analysis_prompt(fused.diseaseLabel, fused.textDescription, contexts)

    # 4. Generate advisory
    advisory = await generate_advisory(prompt)

    # 5. Build result
    now = datetime.now(timezone.utc).isoformat()
    result = AnalysisResult(
        sessionId=session_id,
        disease=classification or DiseaseClassification(
            label="Unknown",
            confidence=0,
            confidenceLevel=ConfidenceLevel.UNKNOWN,
            isKnown=False,
        ),
        advisory=advisory,
        retrievedContext=contexts,
        followUpSuggestions=[
            "What is the recommended dosage for the treatment?",
            "Are there organic alternatives available?",
            "How can I prevent this disease next season?",
            "Could this spread to my other crops?",
        ],
        timestamp=now,
    )

    # 6. Store in Supabase
    store_session(session_id, input_type)
    store_message(session_id, "farmer", text_description, now)
    store_message(session_id, "assistant", advisory, now)
    store_analysis_result(session_id, result.model_dump())

    return result.model_dump()


@router.post("/image")
async def analyze_image(
    image: UploadFile = File(...),
    sessionId: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
):
    """POST /analyze/image — classify image and run advisory pipeline."""
    # Validate image
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/bmp"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format. Allowed: {', '.join(allowed_types)}",
        )

    image_data = await image.read()
    if len(image_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image file must not exceed 10 MB.")

    session_id = sessionId or str(uuid.uuid4())
    logger.info(f"Image analysis request (session={session_id}, size={len(image_data)})")

    # Classify the image
    classification = await classify_image(image_data)

    # Process additional text if provided
    additional = (description or "").strip()
    text_desc = (
        process_text_input(additional)
        if additional
        else f"Image submitted for analysis. Suspected disease: {classification.label}."
    )

    result = await _run_analysis_pipeline(session_id, "image", classification, text_desc)
    return {"success": True, "data": result}


@router.post("/voice")
async def analyze_voice(
    audio: UploadFile = File(...),
    sessionId: Optional[str] = Form(None),
):
    """POST /analyze/voice — transcribe audio and run advisory pipeline."""
    allowed_types = ["audio/wav", "audio/webm", "audio/ogg", "audio/mpeg", "audio/mp4"]
    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format. Allowed: {', '.join(allowed_types)}",
        )

    audio_data = await audio.read()
    if len(audio_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Audio file must not exceed 10 MB.")

    session_id = sessionId or str(uuid.uuid4())
    logger.info(f"Voice analysis request (session={session_id}, size={len(audio_data)})")

    # Transcribe audio
    transcribed = await speech_to_text(audio_data)
    processed = process_text_input(transcribed)

    result = await _run_analysis_pipeline(session_id, "voice", None, processed)
    result["transcribedText"] = transcribed
    return {"success": True, "data": result}


@router.post("/text")
async def analyze_text(body: TextAnalysisRequest):
    """POST /analyze/text — analyze text description and run advisory pipeline."""
    if not body.description or len(body.description.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="A text description of at least 5 characters is required.",
        )

    session_id = body.sessionId or str(uuid.uuid4())
    logger.info(f"Text analysis request (session={session_id})")

    processed = process_text_input(body.description)
    result = await _run_analysis_pipeline(session_id, "text", None, processed)
    return {"success": True, "data": result}
