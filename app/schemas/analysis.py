from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class AnalysisResponse(BaseModel):
    id: int
    user_id: int
    csv_filename: str
    status: str
    results_json: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnalysisResults(BaseModel):
    performance_report: Dict[str, Any]
    ai_insights: list[str]
    next_ad_plan: Dict[str, Any]
    content_strategy: Dict[str, Any]
    creative_prompts: list[str]
    captions_hashtags: list[Dict[str, str]]
