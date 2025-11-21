from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class ReportStatus(enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class ReportSourceType(enum.Enum):
    CSV = "csv"
    SOCIAL_ACCOUNT = "social_account"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_type = Column(Enum(ReportSourceType), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)  # For CSV reports
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True)  # For OAuth reports
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    pdf_path = Column(String, nullable=True)  # Path to generated PDF
    report_data = Column(Text, nullable=True)  # JSON string of report data
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="reports")
    analysis = relationship("Analysis", backref="reports")
    social_account = relationship("SocialAccount", backref="reports")
