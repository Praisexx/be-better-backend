"""
Migration script to add csv_content column to analyses table
Run this manually on production database or via the /api/migrate endpoint
"""
from sqlalchemy import text
from app.database import engine

def add_csv_content_column():
    """Add csv_content column to analyses table if it doesn't exist"""
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='analyses' AND column_name='csv_content';
        """))

        if result.fetchone() is None:
            # Column doesn't exist, add it
            conn.execute(text("""
                ALTER TABLE analyses
                ADD COLUMN csv_content TEXT;
            """))
            conn.commit()
            print("✅ Added csv_content column to analyses table")
        else:
            print("ℹ️  csv_content column already exists")

if __name__ == "__main__":
    add_csv_content_column()
