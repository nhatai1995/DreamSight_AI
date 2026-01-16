"""
Tiered Service System Schemas
Defines tier levels and content masking models for monetization.
"""

from enum import Enum
from typing import Optional, List, Union
from pydantic import BaseModel, Field


class UserTier(str, Enum):
    """User access tier levels."""
    GUEST = "guest"      # Not logged in (IP-based tracking)
    MEMBER = "free"      # Logged in, free tier (maps to DB 'free')
    MASTER = "master"    # Premium tier (full access)


class LockedContent(BaseModel):
    """Placeholder for locked premium content."""
    is_locked: bool = True
    message: str = "🔒 Nâng cấp lên Cao Thủ để mở khóa"
    upgrade_hint: str = "Tarot, Kinh Dịch, Số May Mắn & Lời Khuyên Chi Tiết"


class TieredTriangleResponse(BaseModel):
    """
    Triangle analysis response with tier-based content masking.
    
    - Guest/Member: Only see `psychology` (full)
    - Master: See everything (full access)
    """
    id: str = Field(..., description="Unique analysis ID")
    user_dream: str = Field(..., description="Original dream text")
    user_tier: UserTier = Field(..., description="User's current tier")
    remaining_quota: Optional[int] = Field(
        None, 
        description="Remaining requests for today (null for Master)"
    )
    
    # Psychology: Always visible (Full Access for all tiers)
    psychology: dict = Field(..., description="Full 4-layer psychology analysis")
    
    # Premium content: Locked for Guest/Member, Full for Master
    tarot: Union[dict, LockedContent] = Field(
        ..., 
        description="Tarot reading (locked for non-Master)"
    )
    iching: Union[dict, LockedContent] = Field(
        ..., 
        description="I Ching hexagram analysis (locked for non-Master)"
    )
    synthesis: Union[dict, LockedContent] = Field(
        ..., 
        description="Final synthesis and advice (locked for non-Master)"
    )
    lucky_numbers: Union[List[dict], LockedContent] = Field(
        ..., 
        description="Lucky numbers from Tarot/I Ching/Sổ Mơ (locked for non-Master)"
    )
    
    # Metadata (always visible)
    sources: dict = Field(default_factory=dict, description="Retrieved context sources")
    created_at: str = Field(..., description="ISO timestamp of analysis")


# Quota limits per tier (requests per day)
TIER_QUOTAS = {
    UserTier.GUEST: 1,
    UserTier.MEMBER: 3,
    UserTier.MASTER: None,  # Unlimited
}
