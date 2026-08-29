import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import SessionLocal
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure upload directories exist and initialize database
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.REPORT_OUTPUT_DIR, exist_ok=True)
    
    try:
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Database initialization skipped during startup: %s", str(e))
        
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Legal Metrology Compliance Scanner (Smart India Hackathon 2026)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve uploaded and preprocessed images as static files
# Accessible at: /uploads/raw/{id}/{side}.jpg  and  /uploads/preprocessed/{id}/{side}_processed.jpg
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "status": "online"
    }
