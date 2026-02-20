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
    """Seed common crop diseases found in Kerala into the knowledge base."""
    result = await db.execute(select(DiseaseKnowledge))
    existing = result.scalars().all()
    if existing:
        return

    diseases = [
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Kole Rot (Mahali Disease)",
            symptoms="arecanut rot,mahali,kole rot,nut dropping,immature nut fall,arecanut black spots",
            solution=(
                "Spray 1% Bordeaux mixture before the onset of monsoon (May-June). "
                "Remove and destroy infected bunches. Ensure proper drainage in arecanut gardens. "
                "Apply Metalaxyl-Mancozeb at 2g/L during June-September. "
                "Contact your nearest Krishi Bhavan for guidance."
            ),
            region="Kasaragod, Kannur, Wayanad",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Quick Wilt of Pepper (Phytophthora)",
            symptoms="pepper wilting,black pepper wilt,quick wilt,pepper leaf drop,pepper root rot,kurumulaku",
            solution=(
                "Drench the base with Potassium Phosphonate (3ml/L) or Metalaxyl-Mancozeb (2g/L). "
                "Apply Trichoderma-enriched neem cake at the base. Improve drainage around vines. "
                "Avoid waterlogging during monsoon. Mulch with dried leaves to prevent splash infection. "
                "Recommended by KAU (Kerala Agricultural University)."
            ),
            region="Idukki, Wayanad, Kannur, Kozhikode",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Bud Rot of Coconut",
            symptoms="coconut bud rot,spindle leaf drooping,crown dying,coconut heart rot,thenga choriyuka",
            solution=(
                "Remove the affected portion and apply 10% Bordeaux paste on cut surfaces. "
                "Pour Metalaxyl-Mancozeb solution (2g/L) into the crown. "
                "Apply 2 kg neem cake per palm annually. Ensure adequate spacing between palms. "
                "Report severe cases to the Coconut Development Board or nearest Krishi Bhavan."
            ),
            region="Thiruvananthapuram, Kollam, Alappuzha, Thrissur",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Rice Blast",
            symptoms="rice spots,diamond shaped lesions,gray center,rice blast,panicle blast,nellu roga",
            solution=(
                "Apply Tricyclazole (0.6g/L) at tillering and panicle initiation stages. "
                "Use balanced nitrogen fertilizer - do not over-apply urea. "
                "Maintain 2-3 cm standing water in paddy fields. "
                "Grow blast-resistant varieties like Jyothi, Kanchana, or Uma recommended by KAU."
            ),
            region="Palakkad, Alappuzha, Kuttanad, Thrissur",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Banana Sigatoka Leaf Spot",
            symptoms="banana leaf spots,yellow streaks on banana,sigatoka,vazhakkula roga,banana brown spots",
            solution=(
                "Remove severely affected leaves and destroy them. "
                "Spray Propiconazole (1ml/L) or Carbendazim (1g/L) at 15-day intervals. "
                "Ensure proper spacing between banana plants for air circulation. "
                "Apply adequate potash fertilizer. Nendran and Poovan varieties are susceptible."
            ),
            region="Thrissur, Ernakulam, Kozhikode, Malappuram",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Rhizome Rot of Ginger",
            symptoms="ginger rot,ginger wilting,rhizome rot,soft rot ginger,inji azhukkal",
            solution=(
                "Treat seed rhizomes with Mancozeb (3g/L) for 30 minutes before planting. "
                "Drench affected beds with Copper Oxychloride (3g/L). "
                "Ensure raised beds with good drainage. Avoid waterlogging during heavy monsoon. "
                "Practice crop rotation - do not repeat ginger in same bed for 3 years. "
                "Bio-control: Apply Trichoderma viride enriched FYM."
            ),
            region="Wayanad, Idukki, Kozhikode",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Leaf Blight of Rubber",
            symptoms="rubber leaf fall,abnormal leaf fall,rubber leaf blight,rubber defoliation",
            solution=(
                "Spray Mancozeb (2g/L) or Copper Oxychloride (3g/L) during re-foliation period (January-February). "
                "Use aerial spraying for large estates if available. "
                "Maintain optimum plant density. Apply balanced NPK fertilizers. "
                "Contact the Rubber Board regional office for spraying schedule."
            ),
            region="Kottayam, Ernakulam, Pathanamthitta, Idukki",
            created_at=datetime.utcnow(),
        ),
        DiseaseKnowledge(
            id=uuid.uuid4(),
            disease_name="Cardamom Mosaic (Katte Disease)",
            symptoms="cardamom mosaic,katte disease,cardamom leaf streak,elam roga,green mosaic cardamom",
            solution=(
                "Remove and destroy infected plants immediately. "
                "Control aphid vectors by spraying Dimethoate (2ml/L). "
                "Use virus-free planting material from certified nurseries. "
                "Maintain isolation distance from infected plantations. "
                "Consult the Cardamom Research Station, Pampadumpara for resistant varieties."
            ),
            region="Idukki, Wayanad",
            created_at=datetime.utcnow(),
        ),
    ]

    for disease in diseases:
        db.add(disease)
    await db.commit()
    print(f"Seeded {len(diseases)} Kerala crop diseases into knowledge base")
