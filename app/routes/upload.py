from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analysis import Analysis, AnalysisStatus
from app.routes.auth import oauth2_scheme
from app.utils.auth import decode_access_token
from config import settings
import aiofiles
import os
from datetime import datetime
from app.services.celery_tasks import process_csv_task

router = APIRouter()

async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return payload.get("user_id")

@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )

    # Check file size
    contents = await file.read()
    file_size = len(contents)

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )

    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{user_id}_{timestamp}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_FOLDER, safe_filename)

    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(contents)

    # Create analysis record
    analysis = Analysis(
        user_id=user_id,
        csv_filename=safe_filename,
        status=AnalysisStatus.PENDING
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Trigger async processing with absolute path
    abs_file_path = os.path.abspath(file_path)
    task_result = process_csv_task.delay(analysis.id, abs_file_path)

    return {
        "message": "File uploaded successfully",
        "analysis_id": analysis.id,
        "status": analysis.status.value,
        "task_id": task_result.id
    }

@router.get("/queue-status")
async def get_queue_status(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    pending_analyses = db.query(Analysis).filter(
        Analysis.user_id == user_id,
        Analysis.status.in_([AnalysisStatus.PENDING, AnalysisStatus.PROCESSING])
    ).all()

    return {
        "queue_count": len(pending_analyses),
        "analyses": [
            {
                "id": a.id,
                "filename": a.csv_filename,
                "status": a.status.value,
                "created_at": a.created_at
            }
            for a in pending_analyses
        ]
    }
