from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base, AsyncSessionLocal
from app.seed import seed_superadmin, seed_disease_knowledge
from app.routers import auth_router, user_router, chat_router, mitl_router, admin_router
from app.rag_service import RAGService
from app.models import DiseaseKnowledge

from sqlalchemy import text, select
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Migrate role column from enum to varchar if needed
    async with engine.begin() as conn:
        try:
            await conn.execute(text(
                "ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50) USING role::text"
            ))
            await conn.execute(text(
                "UPDATE users SET role = 'superadmin' WHERE role = 'superuser'"
            ))
            await conn.execute(text("DROP TYPE IF EXISTS userrole"))
        except Exception:
            pass  # Already migrated or table doesn't exist yet
            
        try:
            await conn.execute(text(
                "ALTER TABLE disease_knowledge ALTER COLUMN symptom TYPE TEXT"
            ))
        except Exception:
            pass

    # Create tables & Handle Migration
    async with engine.connect() as conn:
        needs_drop = False
        try:
            await conn.execute(text("SELECT crop FROM disease_knowledge LIMIT 1"))
        except Exception:
            needs_drop = True
            logger.info("Outdated disease_knowledge table detected. Plan: Dropping for recreation.")

    if needs_drop:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS disease_knowledge CASCADE"))
            logger.info("Outdated disease_knowledge table dropped.")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed data and Initialize RAG
    async with AsyncSessionLocal() as db:
        await seed_superadmin(db)
        await seed_disease_knowledge(db)
        
        # Load all knowledge for RAG
        result = await db.execute(select(DiseaseKnowledge))
        knowledge_list = result.scalars().all()
        
        # Initialize RAG Service
        rag_service = RAGService()
        await rag_service.initialize()
        await rag_service.build_index_from_knowledge(knowledge_list)
        app.state.rag_service = rag_service

        # Initialize Translation Service
        from app.translation import TranslationService
        translation_service = TranslationService()
        await translation_service.initialize()
        app.state.translation_service = translation_service
    yield


app = FastAPI(
    title="Farmer Disease Chatbot API",
    description="AI-powered crop disease detection chatbot for farmers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(mitl_router.router)
app.include_router(admin_router.router)


@app.get("/")
async def root():
    return {"message": "Farmer Disease Chatbot API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
