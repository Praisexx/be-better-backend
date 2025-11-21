from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.social_account import SocialAccount, Platform
from app.models.campaign import Campaign
from app.schemas.social_account import (
    OAuthInitiate,
    OAuthCallback,
    SocialAccountResponse,
    PlatformEnum
)
from app.schemas.campaign import CampaignResponse
from app.services.oauth_service import OAuthService
from app.routes.auth import oauth2_scheme
from app.utils.auth import decode_access_token

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user

@router.get("/connected", response_model=List[SocialAccountResponse])
async def get_connected_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all connected social accounts for the current user"""
    accounts = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.is_active == True
    ).all()

    return accounts

@router.post("/oauth/initiate")
async def initiate_oauth(
    oauth_data: OAuthInitiate,
    current_user: User = Depends(get_current_user)
):
    """
    Initiate OAuth flow for a social media platform.
    Returns the authorization URL to redirect the user to.
    """
    try:
        oauth_url_data = OAuthService.generate_oauth_url(oauth_data.platform.value)
        return {
            "authorization_url": oauth_url_data["authorization_url"],
            "state": oauth_url_data["state"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/oauth/callback", response_model=SocialAccountResponse)
async def handle_oauth_callback(
    callback_data: OAuthCallback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback and create/update social account.
    Exchanges the authorization code for an access token.
    """
    try:
        # Exchange code for token
        token_data = await OAuthService.exchange_code_for_token(
            callback_data.platform.value,
            callback_data.code,
            callback_data.state
        )

        # Check if account already exists for this user and platform
        existing_account = db.query(SocialAccount).filter(
            SocialAccount.user_id == current_user.id,
            SocialAccount.platform == Platform[callback_data.platform.value.upper()],
            SocialAccount.platform_user_id == token_data["platform_user_id"]
        ).first()

        if existing_account:
            # Update existing account
            existing_account.access_token = token_data["access_token"]
            existing_account.refresh_token = token_data.get("refresh_token")
            existing_account.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
            existing_account.is_active = True
            existing_account.platform_username = token_data.get("platform_username")
            existing_account.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_account)
            return existing_account

        # Create new account
        new_account = SocialAccount(
            user_id=current_user.id,
            platform=Platform[callback_data.platform.value.upper()],
            platform_user_id=token_data["platform_user_id"],
            platform_username=token_data.get("platform_username"),
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
            is_active=True
        )

        db.add(new_account)
        db.commit()
        db.refresh(new_account)

        return new_account

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}"
        )

@router.delete("/{account_id}")
async def disconnect_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect (deactivate) a social account"""
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    # Soft delete - just deactivate
    account.is_active = False
    account.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Account disconnected successfully"}

@router.post("/{account_id}/sync")
async def sync_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync campaigns from a connected social account"""
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id,
        SocialAccount.is_active == True
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found or inactive"
        )

    try:
        # Fetch campaigns from the platform
        campaigns_data = await OAuthService.get_platform_campaigns(
            account.platform.value,
            account.access_token
        )

        # Update or create campaigns
        synced_count = 0
        for campaign_data in campaigns_data:
            existing_campaign = db.query(Campaign).filter(
                Campaign.social_account_id == account_id,
                Campaign.platform_campaign_id == campaign_data["platform_campaign_id"]
            ).first()

            if existing_campaign:
                # Update existing campaign
                for key, value in campaign_data.items():
                    setattr(existing_campaign, key, value)
                existing_campaign.updated_at = datetime.utcnow()
            else:
                # Create new campaign
                new_campaign = Campaign(
                    social_account_id=account_id,
                    **campaign_data
                )
                db.add(new_campaign)

            synced_count += 1

        # Update last sync time
        account.last_synced_at = datetime.utcnow()
        db.commit()

        return {
            "message": f"Successfully synced {synced_count} campaigns",
            "synced_count": synced_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync campaigns: {str(e)}"
        )

@router.get("/{account_id}/campaigns", response_model=List[CampaignResponse])
async def get_account_campaigns(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all campaigns for a specific social account"""
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    campaigns = db.query(Campaign).filter(
        Campaign.social_account_id == account_id
    ).all()

    return campaigns
