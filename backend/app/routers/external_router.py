from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Dict
from app.database import get_db
from app.models import UnknownDisease, LeafImage
from app.schemas import UnknownDiseaseResponse
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/api/external", tags=["external"])

class PendingImageResponse(BaseModel):
    source: str  # 'unknown_disease' or 'leaf_image'
    id: str | UUID
    image_url: str
    text_symptoms: str | None = None
    created_at: datetime

@router.get("/pending", response_model=List[PendingImageResponse])
async def list_pending_images(db: AsyncSession = Depends(get_db)):
    """
    Returns all pending images from both UnknownDisease and LeafImage tables
    for external review.
    """
    # 1. Get pending from UnknownDisease
    stmt1 = select(UnknownDisease).where(UnknownDisease.status == "pending")
    result1 = await db.execute(stmt1)
    pending_unknowns = result1.scalars().all()
    
    # 2. Get unverified from LeafImage
    stmt2 = select(LeafImage).where(LeafImage.verified == False, LeafImage.predicted == "unknown")
    result2 = await db.execute(stmt2)
    pending_leaves = result2.scalars().all()
    
    combined = []
    
    for item in pending_unknowns:
        combined.append(PendingImageResponse(
            source="unknown_disease",
            id=item.id,
            image_url=item.image_url,
            text_symptoms=item.text_symptoms,
            created_at=item.created_at
        ))
        
    for item in pending_leaves:
        combined.append(PendingImageResponse(
            source="leaf_image",
            id=str(item.id),
            image_url=item.image_path,
            text_symptoms="ResNet flagged - low confidence",
            created_at=item.created_at
        ))
        
    return combined
