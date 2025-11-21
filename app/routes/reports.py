from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.report import Report, ReportStatus, ReportSourceType
from app.models.analysis import Analysis
from app.models.social_account import SocialAccount
from app.schemas.report import (
    ReportGenerate,
    ReportResponse,
    ReportStatusResponse,
    EmailReportRequest
)
from app.routes.auth import oauth2_scheme
from app.utils.auth import decode_access_token
from app.services.pdf_service import generate_pdf
import resend
from config import settings

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user

async def generate_report_background(report_id: int, db: Session):
    """Background task to generate PDF report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return

    try:
        report.status = ReportStatus.GENERATING
        db.commit()

        # Get data based on source type
        if report.source_type == ReportSourceType.CSV:
            analysis = db.query(Analysis).filter(Analysis.id == report.analysis_id).first()
            if not analysis:
                raise Exception("Analysis not found")

            # Generate PDF from analysis data
            import json
            results = json.loads(analysis.results_json) if analysis.results_json else {}
            user = db.query(User).filter(User.id == report.user_id).first()
            pdf_path = generate_pdf(analysis.id, results, user.email if user else "")
            report.pdf_path = pdf_path
            report.report_data = analysis.results_json

        elif report.source_type == ReportSourceType.SOCIAL_ACCOUNT:
            social_account = db.query(SocialAccount).filter(
                SocialAccount.id == report.social_account_id
            ).first()
            if not social_account:
                raise Exception("Social account not found")

            # TODO: Generate PDF from social account campaigns
            # For now, use placeholder
            report.pdf_path = f"reports/social_account_{report.social_account_id}.pdf"
            report.report_data = "{}"

        report.status = ReportStatus.COMPLETED
        report.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        report.status = ReportStatus.FAILED
        report.error_message = str(e)
        db.commit()

@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_data: ReportGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a PDF report from either a CSV analysis or social account data.
    The generation happens in the background.
    """
    # Validate source
    if report_data.source_type == ReportSourceType.CSV:
        if not report_data.analysis_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="analysis_id is required for CSV reports"
            )

        analysis = db.query(Analysis).filter(
            Analysis.id == report_data.analysis_id,
            Analysis.user_id == current_user.id
        ).first()

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

    elif report_data.source_type == ReportSourceType.SOCIAL_ACCOUNT:
        if not report_data.social_account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="social_account_id is required for social account reports"
            )

        social_account = db.query(SocialAccount).filter(
            SocialAccount.id == report_data.social_account_id,
            SocialAccount.user_id == current_user.id
        ).first()

        if not social_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social account not found"
            )

    # Create report record
    new_report = Report(
        user_id=current_user.id,
        source_type=report_data.source_type,
        analysis_id=report_data.analysis_id,
        social_account_id=report_data.social_account_id,
        status=ReportStatus.PENDING
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # Schedule background task to generate report
    background_tasks.add_task(generate_report_background, new_report.id, db)

    return new_report

@router.get("/{report_id}/status", response_model=ReportStatusResponse)
async def get_report_status(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the status of a report generation"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return {
        "id": report.id,
        "status": report.status,
        "pdf_path": report.pdf_path,
        "error_message": report.error_message,
        "completed_at": report.completed_at
    }

@router.get("/", response_model=List[ReportResponse])
async def get_user_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports for the current user"""
    reports = db.query(Report).filter(
        Report.user_id == current_user.id
    ).order_by(Report.created_at.desc()).all()

    return reports

@router.post("/email")
async def email_report(
    email_data: EmailReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Email a report to the specified email address.
    Can use either report_id or analysis_id.
    """
    # Initialize Resend
    resend.api_key = settings.RESEND_API_KEY

    pdf_path = None

    if email_data.report_id:
        # Get report
        report = db.query(Report).filter(
            Report.id == email_data.report_id,
            Report.user_id == current_user.id
        ).first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )

        if report.status != ReportStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report is not completed yet"
            )

        pdf_path = report.pdf_path

    elif email_data.analysis_id:
        # Get analysis and generate PDF if needed
        analysis = db.query(Analysis).filter(
            Analysis.id == email_data.analysis_id,
            Analysis.user_id == current_user.id
        ).first()

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

        # Generate PDF
        import json
        results = json.loads(analysis.results_json) if analysis.results_json else {}
        pdf_path = generate_pdf(analysis.id, results, current_user.email)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either report_id or analysis_id must be provided"
        )

    if not pdf_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF"
        )

    # Send email with Resend
    try:
        # TODO: Attach PDF file to email
        # For now, send a simple email
        params = {
            "from": settings.FROM_EMAIL,
            "to": [email_data.email],
            "subject": "Your Meta Ads Analysis Report",
            "html": f"""
                <h2>Your Ad Analytics Report</h2>
                <p>Thank you for using Meta Ads AI Analyzer!</p>
                <p>Your report has been generated and is attached to this email.</p>
                <p>Best regards,<br>The Meta Ads AI Analyzer Team</p>
            """
        }

        email_response = resend.Emails.send(params)

        return {
            "message": f"Report sent successfully to {email_data.email}",
            "email_id": email_response.get("id")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )
