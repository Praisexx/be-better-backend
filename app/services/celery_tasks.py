from app.services.celery_app import celery_app
from app.database import SessionLocal
from app.models.analysis import Analysis, AnalysisStatus
from app.utils.csv_parser import parse_meta_ads_csv, format_metrics_for_ai
from app.services.openai_service import analyze_meta_ads
from app.services.email_service import send_analysis_email
from app.services.pdf_service import generate_pdf
from datetime import datetime
import json
import os

@celery_app.task(name="process_csv_task")
def process_csv_task(analysis_id: int, file_path: str):
    """
    Background task to process CSV file, analyze with AI, and send results
    """
    db = SessionLocal()
    analysis = None

    try:
        # Get analysis record
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return {"error": "Analysis not found"}

        # Update status to processing
        analysis.status = AnalysisStatus.PROCESSING
        db.commit()

        # Parse CSV
        print(f"Parsing CSV file: {file_path}")
        parsed_data = parse_meta_ads_csv(file_path)

        # Format for AI
        print(f"Formatting data for AI analysis")
        ai_prompt = format_metrics_for_ai(parsed_data)

        # Get AI analysis
        print(f"Running AI analysis for analysis {analysis_id}")
        ai_results = analyze_meta_ads(ai_prompt)

        # Store results and mark as completed
        analysis.results_json = json.dumps(ai_results)
        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"Analysis {analysis_id} completed successfully")

        # === Optional post-processing (failures here don't affect analysis status) ===
        
        # Generate PDF (non-critical)
        pdf_path = None
        try:
            print(f"Generating PDF for analysis {analysis_id}")
            pdf_path = generate_pdf(analysis_id, ai_results, analysis.user.email)
            print(f"PDF generated successfully")
        except Exception as pdf_error:
            print(f"Warning: PDF generation failed: {pdf_error}")

        # Send email (non-critical)
        try:
            print(f"Sending email notification for analysis {analysis_id}")
            send_analysis_email(
                to_email=analysis.user.email,
                analysis_id=analysis_id,
                results=ai_results,
                pdf_path=pdf_path
            )
            print(f"Email sent successfully")
        except Exception as email_error:
            print(f"Warning: Email sending failed (this is OK, analysis still completed): {email_error}")

        # Cleanup uploaded CSV file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up CSV file: {file_path}")
        except Exception as cleanup_error:
            print(f"Warning: File cleanup failed: {cleanup_error}")

        return {"status": "success", "analysis_id": analysis_id}

    except Exception as e:
        # Core analysis failed
        print(f"CRITICAL ERROR in process_csv_task for analysis {analysis_id}: {e}")
        
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            db.commit()
            
        return {"status": "failed", "error": str(e)}

    finally:
        db.close()
