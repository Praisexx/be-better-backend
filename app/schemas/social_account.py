from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class PlatformEnum(str, Enum):
    meta = "meta"
    twitter = "twitter"
    linkedin = "linkedin"
    whatsapp = "whatsapp"
    pinterest = "pinterest"
    telegram = "telegram"

class OAuthInitiate(BaseModel):
    platform: PlatformEnum

class OAuthCallback(BaseModel):
    platform: PlatformEnum
    code: str
    state: str

class SocialAccountBase(BaseModel):
    platform: PlatformEnum
    platform_username: Optional[str] = None

class SocialAccountCreate(SocialAccountBase):
    platform_user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None

class SocialAccountResponse(SocialAccountBase):
    id: int
    user_id: int
    platform_user_id: str
    platform_username: Optional[str]
    is_active: bool
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SocialAccountUpdate(BaseModel):
    is_active: Optional[bool] = None
    last_synced_at: Optional[datetime] = None
