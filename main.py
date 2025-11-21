from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
import os

# Create upload folder
if not os.path.exists(settings.UPLOAD_FOLDER):
    os.makedirs(settings.UPLOAD_FOLDER)

app = FastAPI(title=settings.APP_NAME)

# Create database tables on startup
from app.database import engine, Base
from app.models import user, analysis
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routes import auth, upload, analysis

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

# Temporary Seed Endpoint
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.seed import seed_database

@app.post("/api/seed")
async def seed_db_endpoint(db: Session = Depends(get_db)):
    return seed_database(db)

@app.get("/")
async def root():
    return {"message": "Meta Ads AI Analyzer API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
