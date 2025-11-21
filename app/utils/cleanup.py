from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.analysis import Analysis

def delete_analyses_in_range(start_id: int, end_id: int):
    db = SessionLocal()
    try:
        analyses = db.query(Analysis).filter(Analysis.id >= start_id, Analysis.id <= end_id).all()
        count = len(analyses)
        for analysis in analyses:
            db.delete(analysis)
        db.commit()
        print(f"Deleted {count} analyses (IDs {start_id}-{end_id})")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Delete the broken batch (21-40)
    # Also deleting 1-20 just to be clean if you want, but user asked for "broken seeds"
    # I'll delete 21-40 as requested.
    delete_analyses_in_range(21, 40)
