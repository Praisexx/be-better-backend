from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False)
    platform_campaign_id = Column(String, nullable=False)  # Campaign ID from the platform
    campaign_name = Column(String, nullable=False)
    status = Column(String, nullable=True)  # active, paused, completed
    budget = Column(Float, nullable=True)
    spend = Column(Float, nullable=True)
    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    conversions = Column(Integer, nullable=True)
    ctr = Column(Float, nullable=True)  # Click-through rate
    cpc = Column(Float, nullable=True)  # Cost per click
    cpm = Column(Float, nullable=True)  # Cost per mille (thousand impressions)
    platform_data = Column(JSON, nullable=True)  # Additional platform-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    social_account = relationship("SocialAccount", back_populates="campaigns")
