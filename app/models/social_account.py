from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class Platform(enum.Enum):
    META = "meta"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    PINTEREST = "pinterest"
    TELEGRAM = "telegram"

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    platform_user_id = Column(String, nullable=False)  # User ID from the platform
    platform_username = Column(String, nullable=True)  # Username/handle
    access_token = Column(Text, nullable=False)  # OAuth access token (encrypted in production)
    refresh_token = Column(Text, nullable=True)  # OAuth refresh token
    token_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="social_accounts")
    campaigns = relationship("Campaign", back_populates="social_account", cascade="all, delete-orphan")
