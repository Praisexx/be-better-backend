from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class CampaignBase(BaseModel):
    platform_campaign_id: str
    campaign_name: str
    status: Optional[str] = None
    budget: Optional[float] = None
    spend: Optional[float] = None
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    ctr: Optional[float] = None
    cpc: Optional[float] = None
    cpm: Optional[float] = None
    platform_data: Optional[Dict[str, Any]] = None

class CampaignCreate(CampaignBase):
    social_account_id: int

class CampaignResponse(CampaignBase):
    id: int
    social_account_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CampaignUpdate(BaseModel):
    campaign_name: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    spend: Optional[float] = None
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    ctr: Optional[float] = None
    cpc: Optional[float] = None
    cpm: Optional[float] = None
    platform_data: Optional[Dict[str, Any]] = None
