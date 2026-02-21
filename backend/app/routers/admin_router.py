from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database import get_db
from app.models import User, UserRole
from app.deps import get_superadmin
from app.auth import hash_password
from app.schemas import UserResponse, CreateMitlRequest
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """List all users in the system."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
    )
    return [UserResponse.model_validate(u) for u in result.scalars().all()]


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """Get admin dashboard stats."""
    total = await db.execute(select(func.count()).select_from(User))
    farmers = await db.execute(
        select(func.count()).select_from(User).where(User.role == UserRole.farmer)
    )
    mitl = await db.execute(
        select(func.count()).select_from(User).where(User.role == UserRole.mitl)
    )
    return {
        "total_users": total.scalar() or 0,
        "total_farmers": farmers.scalar() or 0,
        "total_mitl": mitl.scalar() or 0,
    }


@router.post("/create-mitl", response_model=UserResponse)
async def create_mitl_account(
    req: CreateMitlRequest,
    current_user: User = Depends(get_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new man-in-the-loop account."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == req.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        id=uuid.uuid4(),
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=UserRole.mitl,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserResponse.model_validate(new_user)
