"""Ad tracking endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.ad_view import AdView
from backend.models.user import User
from backend.auth.dependencies import get_current_user_optional


router = APIRouter(prefix="/api", tags=["ads"])


class AdViewRequest(BaseModel):
    """Request body for logging ad view"""
    sessionId: Optional[str] = None  # For guest users
    skipped: bool


class AdViewResponse(BaseModel):
    """Response for ad view logging"""
    id: str
    userId: Optional[str]
    sessionId: Optional[str]
    actionCount: int
    viewedAt: datetime
    skipped: bool


class ShouldShowAdResponse(BaseModel):
    """Response for should-show-ad check"""
    shouldShowAd: bool
    actionCount: int


@router.post("/ad-view", response_model=AdViewResponse, status_code=status.HTTP_201_CREATED)
async def log_ad_view(
    request: AdViewRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Log an ad view/impression.

    Tracks when ads are shown and whether they were skipped.
    Works for both authenticated users and guest sessions.
    """

    # Count previous actions for this user/session
    if current_user:
        action_count = db.query(AdView)\
            .filter(AdView.user_id == current_user.id)\
            .count() + 1
        session_id = None
        user_id = current_user.id
    else:
        if not request.sessionId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sessionId required for guest users"
            )
        action_count = db.query(AdView)\
            .filter(AdView.session_id == request.sessionId)\
            .count() + 1
        session_id = request.sessionId
        user_id = None

    # Create ad view record
    ad_view = AdView(
        user_id=user_id,
        session_id=session_id,
        action_count=action_count,
        skipped=request.skipped
    )

    db.add(ad_view)
    db.commit()
    db.refresh(ad_view)

    return AdViewResponse(
        id=str(ad_view.id),
        userId=str(ad_view.user_id) if ad_view.user_id else None,
        sessionId=ad_view.session_id,
        actionCount=ad_view.action_count,
        viewedAt=ad_view.viewed_at,
        skipped=ad_view.skipped
    )


@router.get("/should-show-ad", response_model=ShouldShowAdResponse)
async def should_show_ad(
    sessionId: Optional[str] = None,
    actionCount: Optional[int] = None,
    isPremium: Optional[bool] = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Check if an ad should be shown for this user/session.

    Business logic:
    - First action (upload): FREE, no ad
    - Subsequent actions (re-score): Show ad
    - Premium users: Never show ads

    Query params:
    - sessionId: For guest users (required if not authenticated)
    - actionCount: Current action count (optional, will query DB if not provided)
    - isPremium: Override premium status (for testing)
    """

    # Premium users never see ads
    if current_user and current_user.is_premium:
        return ShouldShowAdResponse(shouldShowAd=False, actionCount=0)

    if isPremium:
        return ShouldShowAdResponse(shouldShowAd=False, actionCount=0)

    # Get action count
    if actionCount is not None:
        # Use provided count (for efficiency)
        current_action_count = actionCount
    else:
        # Query database
        if current_user:
            current_action_count = db.query(AdView)\
                .filter(AdView.user_id == current_user.id)\
                .count()
        elif sessionId:
            current_action_count = db.query(AdView)\
                .filter(AdView.session_id == sessionId)\
                .count()
        else:
            # New guest user, first action
            current_action_count = 0

    # Show ad if actionCount >= 2 (i.e., after first free score)
    should_show = current_action_count >= 2

    return ShouldShowAdResponse(
        shouldShowAd=should_show,
        actionCount=current_action_count
    )
