from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import engine, Base
from database import models

from routes.auth import router as auth_router
from routes.profile import router as profile_router
from routes.settings import router as settings_router
from routes.dashboard import router as dashboard_router
from routes.bugs import router as bugs_router
from routes.knowledge import router as knowledge_router


# =========================================================
# DATABASE
# =========================================================

# Create database tables
Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="BugSense API",
    description="AI Smart Bug Analyzer & Fix Advisor Backend",
    version="1.0.0"
)


# =========================================================
# API ROUTERS
# =========================================================

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(settings_router)
app.include_router(dashboard_router)
app.include_router(bugs_router)
app.include_router(knowledge_router)


# =========================================================
# CORS CONFIGURATION
# =========================================================

# Allow BugSense frontend environments to communicate with the backend.
# Local origins are used during development.
# The Vercel origin is used by the deployed production frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://bugsenseproject-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# ROOT API
# =========================================================

@app.get("/")
def root():
    return {
        "message": "BugSense backend is running"
    }


# =========================================================
# HEALTH CHECK API
# =========================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "BugSense API"
    }