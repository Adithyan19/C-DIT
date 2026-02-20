"""Seed the database with the superadmin account and sample disease knowledge."""

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
    """Seed some common crop diseases into the knowledge base."""
    result = await db.execute(select(DiseaseKnowledge))
    existing = result.scalars().all()
    if existing:
        return

    diseases = [
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Late Blight",
            symptoms="dark spots,water soaked lesions,white mold,potato blight,tomato blight",
            solution=(
                "Apply chlorothalonil or mancozeb fungicide immediately. Remove infected plants. "
                "Avoid overhead watering. Plant resistant varieties next season."
            ),
            region="Tropical/Subtropical",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Rice Blast",
            symptoms="rice spots,diamond shaped lesions,gray center,rice blast,panicle blast",
            solution=(
                "Apply tricyclazole fungicide at 0.6g/L. Use balanced nitrogen fertilizer. "
                "Ensure proper water management. Grow blast-resistant rice varieties."
            ),
            region="South/Southeast Asia",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Bacterial Wilt",
            symptoms="sudden wilting,bacterial ooze,stem rot,brown vascular,wilting tomato",
            solution=(
                "No chemical cure available. Remove and destroy infected plants immediately. "
                "Solarize soil for 4-6 weeks. Use resistant rootstock. Practice 3-year crop rotation."
            ),
            region="Worldwide",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Anthracnose",
            symptoms="sunken lesions,dark spots on fruit,anthracnose,mango spots,pepper spots",
            solution=(
                "Apply azoxystrobin or copper-based fungicide. Prune to improve air circulation. "
                "Harvest fruits at proper maturity. Avoid wounding fruits during harvest."
            ),
            region="Tropical",
            created_at=datetime.utcnow(),
        ),
    ]

    for disease in diseases:
        db.add(disease)
    await db.commit()
    print(f"Seeded {len(diseases)} diseases into knowledge base")
