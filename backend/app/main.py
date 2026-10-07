"""
FastAPI entrypoint for VibeCheck-AI.
Mounts API routes and serves the frontend dashboard.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import router

app = FastAPI(
    title="VibeCheck-AI Backend",
    description="Adaptive Multimodal Content-Risk Detection & Multi-Platform Policy Engine for Hindi-English Social Media Videos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Mount frontend files for convenience
frontend_dir = settings.BASE_DIR.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")