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
from app.models import user, analysis, social_account, campaign, report
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
from app.routes import auth, upload, analysis, accounts, reports

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# Temporary Seed Endpoint
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.seed import seed_database

@app.post("/api/seed")
async def seed_data(db: Session = Depends(get_db)):
    from app.utils.seed import seed_database
    return seed_database(db)

@app.delete("/api/cleanup")
async def cleanup_data(db: Session = Depends(get_db)):
    from app.models.analysis import Analysis
    # Delete broken analyses 21-40
    db.query(Analysis).filter(Analysis.id >= 21, Analysis.id <= 40).delete(synchronize_session=False)
    db.commit()
    return {"message": "Deleted broken analyses 21-40"}

@app.get("/")
async def root():
    return {"message": "Meta Ads AI Analyzer API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
