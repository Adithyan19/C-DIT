from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import User, UserRole, UnknownDisease, DiseaseKnowledge, Conversation
from app.deps import get_mitl_user
from app.schemas import (
    UnknownDiseaseResponse,
    ClassifyDiseaseRequest,
    DashboardStatsResponse,
)
from app.disease_engine import diagnostic_engine
import uuid

router = APIRouter(prefix="/api/mitl", tags=["man-in-the-loop"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_stats(
    current_user: User = Depends(get_mitl_user),
    db: AsyncSession = Depends(get_db),
):
    pending = await db.execute(
        select(func.count()).select_from(UnknownDisease).where(
            UnknownDisease.status == "pending"
        )
    )
    classified = await db.execute(
        select(func.count()).select_from(UnknownDisease).where(
            UnknownDisease.status == "classified"
        )
    )
    farmers = await db.execute(
        select(func.count()).select_from(User).where(User.role == UserRole.farmer)
    )
    conversations = await db.execute(
        select(func.count()).select_from(Conversation)
    )

    return DashboardStatsResponse(
        pending_count=pending.scalar() or 0,
        classified_count=classified.scalar() or 0,
        total_farmers=farmers.scalar() or 0,
        total_conversations=conversations.scalar() or 0,
    )


@router.get("/pending", response_model=List[UnknownDiseaseResponse])
async def list_pending(
    current_user: User = Depends(get_mitl_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UnknownDisease)
        .where(UnknownDisease.status == "pending")
        .order_by(UnknownDisease.created_at.desc())
    )
    return [UnknownDiseaseResponse.model_validate(d) for d in result.scalars().all()]


@router.get("/classified", response_model=List[UnknownDiseaseResponse])
async def list_classified(
    current_user: User = Depends(get_mitl_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UnknownDisease)
        .where(UnknownDisease.status == "classified")
        .order_by(UnknownDisease.classified_at.desc())
    )
    return [UnknownDiseaseResponse.model_validate(d) for d in result.scalars().all()]


@router.get("/pending/{disease_id}", response_model=UnknownDiseaseResponse)
async def get_pending_detail(
    disease_id: str,
    current_user: User = Depends(get_mitl_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UnknownDisease).where(UnknownDisease.id == disease_id)
    )
    disease = result.scalar_one_or_none()
    if not disease:
        raise HTTPException(status_code=404, detail="Unknown disease not found")
    return UnknownDiseaseResponse.model_validate(disease)


@router.post("/classify/{disease_id}", response_model=UnknownDiseaseResponse)
async def classify_disease(
    disease_id: str,
    req: ClassifyDiseaseRequest,
    request: Request,
    current_user: User = Depends(get_mitl_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UnknownDisease).where(UnknownDisease.id == disease_id)
    )
    disease = result.scalar_one_or_none()
    if not disease:
        raise HTTPException(status_code=404, detail="Unknown disease not found")

    # Update the unknown disease record
    disease.disease_name = req.disease_name
    disease.solution = req.solution
    disease.status = "classified"
    disease.classified_by = current_user.id
    disease.classified_at = datetime.utcnow()

    # Extract features from symptoms to populate structured columns
    features = diagnostic_engine.extract_features(disease.text_symptoms or "")

    # Add to disease knowledge base so RAG can use it in the future
    knowledge = DiseaseKnowledge(
        id=uuid.uuid4(),
        crop=features["crop"] or "Unknown",
        disease_name=req.disease_name,
        symptom=disease.text_symptoms or "",
        position=features["position"] or None,
        pattern=features["pattern"] or None,
        weather=features["weather"] or None,
        treatment_summary=req.solution,
        image_urls=[disease.image_url] if disease.image_url else [],
        region=req.region,
        created_at=datetime.utcnow(),
    )
    db.add(knowledge)
    await db.commit()
    await db.refresh(disease)

    # Immediately rebuild the RAG index to include the newly classified disease
    if hasattr(request.app.state, "rag_service"):
        rag_service = request.app.state.rag_service
        # Run rebuild as background task so we don't block the API response
        import asyncio
        asyncio.create_task(rag_service.rebuild_index(db))
    
    return UnknownDiseaseResponse.model_validate(disease)
