"""Seed the database with the superadmin account and Kerala-specific disease knowledge."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, UserRole, DiseaseKnowledge
from app.auth import hash_password
from app.config import settings
import uuid
from datetime import datetime


async def seed_superadmin(db: AsyncSession):
    """Create the hardcoded superadmin if it doesn't exist."""
    result = await db.execute(
        select(User).where(User.email == settings.SUPERUSER_EMAIL)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return

    superadmin = User(
        id=uuid.uuid4(),
        email=settings.SUPERUSER_EMAIL,
        password_hash=hash_password(settings.SUPERUSER_PASSWORD),
        full_name=settings.SUPERUSER_NAME,
        role=UserRole.superadmin,
        created_at=datetime.utcnow(),
    )
    db.add(superadmin)
    await db.commit()
    print(f"Superadmin created: {settings.SUPERUSER_EMAIL}")


async def seed_disease_knowledge(db: AsyncSession):
    """Seed the database with the structured disease knowledge."""
    # Check if we already have knowledge seeded
    result = await db.execute(select(DiseaseKnowledge))
    if result.scalars().first():
        return

    knowledge_items = [
        {
            "crop": "tomato",
            "disease_name": "early blight",
            "symptom": "brown lesion",
            "position": "lower leaves",
            "pattern": "concentric rings",
            "weather": "humid",
            "treatment_summary": "Apply Chlorothalonil or copper-based fungicides. Remove infected lower leaves."
        },
        {
            "crop": "coconut",
            "disease_name": "root wilt",
            "symptom": "yellowing",
            "position": "lower leaves",
            "pattern": "wilting",
            "weather": "humid",
            "treatment_summary": "Apply balanced fertilizers (NPK) and improve drainage. 1 kg Urea 2 kg Superphosphate 2 kg Potash per palm per year."
        },
        {
            "crop": "pepper",
            "disease_name": "quick wilt",
            "symptom": "dark spots",
            "position": "leaves",
            "pattern": "rapid wilt",
            "weather": "rainy",
            "treatment_summary": "Soil drenching with 0.2% copper oxychloride or 1% Bordeaux mixture."
        },
        {
            "crop": "banana",
            "disease_name": "sigatoka",
            "symptom": "yellow borders",
            "position": "leaves",
            "pattern": "streaks",
            "weather": "rainy",
            "treatment_summary": "Spray 1% Bordeaux mixture or 0.2% Carbendazim. Improve leaf sanitation."
        },
        {
            "crop": "rice",
            "disease_name": "bacterial leaf blight",
            "symptom": "burnt tips",
            "position": "leaves",
            "pattern": "streaks",
            "weather": "humid",
            "treatment_summary": "Avoid excess nitrogen. Spray 20g Streptomycin + 200g Copper Oxychloride in 100L water."
        },
        {
            "crop": "arecanut",
            "disease_name": "yellow leaf disease",
            "symptom": "yellowing",
            "position": "mid leaves",
            "pattern": "rot",
            "weather": "rainy",
            "treatment_summary": "Improve drainage and apply 10kg organic manure + 5g Borax per palm."
        },
        {
            "crop": "ginger",
            "disease_name": "soft rot",
            "symptom": "yellowing",
            "position": "rhizome",
            "pattern": "soft rot",
            "weather": "monsoon",
            "treatment_summary": "Seed treatment with Mancozeb. Soil drenching with 1% Bordeaux mixture."
        },
        {
            "crop": "tapioca",
            "disease_name": "cassava mosaic",
            "symptom": "mosaic",
            "position": "leaves",
            "pattern": "mottling",
            "weather": "dry",
            "treatment_summary": "Use mosaic-free stem cuttings. Remove infected plants. Control whiteflies with Neem oil."
        },
    ]

    for item in knowledge_items:
        db.add(DiseaseKnowledge(**item))
    
    await db.commit()
    print("Predefined disease knowledge seeded.")