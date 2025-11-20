from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analysis import Analysis
from app.routes.auth import oauth2_scheme
from app.utils.auth import decode_access_token
from app.schemas.analysis import AnalysisResponse
from app.services.pdf_service import generate_pdf
from typing import List
import json
import os

router = APIRouter()

async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return payload.get("user_id")

@router.get("/history", response_model=List[AnalysisResponse])
async def get_analysis_history(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    limit: int = 10
):
    """Get user's analysis history"""
    analyses = db.query(Analysis).filter(
        Analysis.user_id == user_id
    ).order_by(Analysis.created_at.desc()).limit(limit).all()

    return analyses

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get specific analysis details"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return analysis

@router.get("/{analysis_id}/results")
async def get_analysis_results(
    analysis_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get parsed analysis results (JSON format)"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    if not analysis.results_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis not completed yet"
        )

    return json.loads(analysis.results_json)

@router.get("/{analysis_id}/download-pdf")
async def download_pdf(
    analysis_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Download analysis as PDF"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    if not analysis.results_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis not completed yet"
        )

    # Generate PDF
    results = json.loads(analysis.results_json)
    pdf_path = generate_pdf(analysis_id, results, analysis.user.email)

    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating PDF"
        )

    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"meta_ads_analysis_{analysis_id}.pdf"
    )

@router.post("/{analysis_id}/download-pdf-with-charts")
async def download_pdf_with_charts(
    analysis_id: int,
    request_data: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Download analysis as PDF with charts"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    if not analysis.results_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis not completed yet"
        )

    # Generate PDF with charts
    results = json.loads(analysis.results_json)
    chart_images = request_data.get('chart_images', {})
    
    from app.services.pdf_service import generate_pdf_with_charts
    pdf_path = generate_pdf_with_charts(analysis_id, results, analysis.user.email, chart_images)

    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating PDF"
        )

    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"meta_ads_analysis_{analysis_id}.pdf"
    )

@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete an analysis"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    db.delete(analysis)
    db.commit()

    return {"message": "Analysis deleted successfully"}
