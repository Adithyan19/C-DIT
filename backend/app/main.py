from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base, AsyncSessionLocal
from app.seed import seed_superadmin, seed_disease_knowledge
from app.routers import auth_router, user_router, chat_router, mitl_router, admin_router

from sqlalchemy import text


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

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed data
    async with AsyncSessionLocal() as db:
        await seed_superadmin(db)
        await seed_disease_knowledge(db)
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
