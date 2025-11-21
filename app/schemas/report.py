from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class ReportStatusEnum(str, Enum):
    pending = "pending"
    generating = "generating"
    completed = "completed"
    failed = "failed"

class ReportSourceTypeEnum(str, Enum):
    csv = "csv"
    social_account = "social_account"

class ReportGenerate(BaseModel):
    source_type: ReportSourceTypeEnum
    analysis_id: Optional[int] = None
    social_account_id: Optional[int] = None

class ReportResponse(BaseModel):
    id: int
    user_id: int
    source_type: ReportSourceTypeEnum
    analysis_id: Optional[int]
    social_account_id: Optional[int]
    status: ReportStatusEnum
    pdf_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReportStatusResponse(BaseModel):
    id: int
    status: ReportStatusEnum
    pdf_path: Optional[str]
    error_message: Optional[str]
    completed_at: Optional[datetime]

class EmailReportRequest(BaseModel):
    email: EmailStr
    report_id: Optional[int] = None
    analysis_id: Optional[int] = None
