"""
Dreams Router
API endpoints for dream interpretation and symbol search.
Production-hardened with rate limiting, auth, API key security, and structured logging.
"""

from typing import Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import get_settings
from models.schemas import (
    DreamInterpretationRequest,
    DreamInterpretationResponse,
    DreamSearchRequest,
    DreamSearchResponse,
    ErrorResponse,
    AnalyzeDreamRequest,
    AnalyzeDreamResponse,
)
from services.dream_service import analysis_triangle_service, TriangleAnalysisResponse
from services.analyze_service import analyze_dream_service
from services.db_service import (
    verify_user_token, 
    save_dream_to_db, 
    get_user_dreams,
    get_user_profile,
    check_guest_quota,
    check_member_quota,
    increment_member_usage,
)
from models.tier_schemas import UserTier, LockedContent, TieredTriangleResponse, TIER_QUOTAS
from utils.logger import log_info, log_error, log_warning

settings = get_settings()
router = APIRouter()

# Initialize limiter (attached to app in main.py)
limiter = Limiter(key_func=get_remote_address)


# ============================================
# API Key Verification Dependency
# ============================================

async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> str:
    """
    Verify the static API key from X-API-Key header.
    This runs for ALL requests to prevent unauthorized access.
    
    Raises:
        HTTPException 403: If API key is missing or invalid
    """
    # Check if API key is configured
    if not settings.api_secret_key:
        # API key not set in config - skip verification (development mode)
        log_warning("API_SECRET_KEY not configured - skipping API key verification")
        return "dev_mode"
    
    # Check if header is provided
    if not x_api_key:
        log_warning("Request blocked: Missing X-API-Key header")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key required. Please provide X-API-Key header.",
        )
    
    # Verify the key
    if x_api_key != settings.api_secret_key:
        log_warning(f"Request blocked: Invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
    
    return x_api_key


# ============================================
# Helper Functions
# ============================================

def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """
    Extract the JWT token from the Authorization header.
    
    Args:
        authorization: The full Authorization header value
        
    Returns:
        The token string if present, None otherwise
    """
    if not authorization:
        return None
    
    # Expected format: "Bearer <token>"
    parts = authorization.split(" ")
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    
    return None


# ============================================
# Endpoints
# ============================================

@router.post(
    "/interpret",
    response_model=DreamInterpretationResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="Interpret a dream",
    description="Analyze and interpret a dream using AI and the dream knowledge base.",
    dependencies=[Depends(verify_api_key)],
)
async def interpret_dream(request: DreamInterpretationRequest):
    """
    Interpret a dream and provide insights.
    
    - **dream_text**: The dream narrative to interpret (10-500 characters)
    - **include_symbols**: Whether to include symbol analysis
    - **language**: Response language (default: en)
    """
    log_info(f"Interpret request received - length: {len(request.dream_text)} chars")
    
    try:
        result = await dream_service.interpret_dream(request)
        log_info("Interpret request completed successfully")
        return result
    except ValueError as e:
        log_error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        log_error(f"Interpret service error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Oracle is meditating (Service busy). Please try again.",
        )


@router.post(
    "/search",
    response_model=DreamSearchResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        500: {"model": ErrorResponse},
    },
    summary="Search dream symbols",
    description="Search the dream knowledge base for symbol meanings.",
    dependencies=[Depends(verify_api_key)],
)
async def search_symbols(request: DreamSearchRequest):
    """
    Search for dream symbols in the knowledge base.
    
    - **query**: Search query for dream symbols
    - **limit**: Maximum number of results (1-20)
    """
    log_info(f"Search request: '{request.query}'")
    
    try:
        result = await dream_service.search_symbols(request)
        log_info(f"Search completed - {len(result.results)} results")
        return result
    except ValueError as e:
        log_error(f"Search validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        log_error(f"Search service error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Oracle is meditating (Service busy). Please try again.",
        )


@router.get(
    "/symbols/common",
    summary="Get common dream symbols",
    description="Get a list of commonly analyzed dream symbols.",
    dependencies=[Depends(verify_api_key)],
)
async def get_common_symbols():
    """Get a list of common dream symbols for reference."""
    log_info("Common symbols request")
    return {
        "symbols": [
            {"name": "Water", "category": "Nature", "meaning": "Emotions, subconscious"},
            {"name": "Flying", "category": "Action", "meaning": "Freedom, ambition"},
            {"name": "Falling", "category": "Action", "meaning": "Loss of control, anxiety"},
            {"name": "House", "category": "Place", "meaning": "Self, psyche"},
            {"name": "Snake", "category": "Animal", "meaning": "Transformation, fear"},
            {"name": "Death", "category": "Event", "meaning": "Endings, new beginnings"},
            {"name": "Teeth", "category": "Body", "meaning": "Confidence, appearance"},
            {"name": "Chase", "category": "Action", "meaning": "Avoidance, pressure"},
            {"name": "Fire", "category": "Element", "meaning": "Passion, destruction"},
            {"name": "Baby", "category": "Person", "meaning": "New beginnings, vulnerability"},
        ]
    }


@router.post(
    "/analyze",
    response_model=AnalyzeDreamResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    summary="Analyze dream with RAG and generate image prompt",
    description="""
Analyze a dream using RAG (Retrieval-Augmented Generation) to provide 
a rich interpretation based on dream dictionaries, Tarot, and I Ching wisdom.

**Security**: Requires X-API-Key header.
**Rate Limited**: 5 requests per minute per IP.
**Max Length**: 500 characters to save tokens.
**Authentication**: Optional. If a valid Bearer token is provided, the dream will be saved to the user's history.

Also generates a Surrealist/Dalí-style image prompt to visualize the dream.
    """,
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(f"{settings.rate_limit_requests}/{settings.rate_limit_window}")
async def analyze_dream(
    dream_request: AnalyzeDreamRequest,
    request: Request,  # Required for slowapi - MUST be named 'request'
    authorization: Optional[str] = Header(None, description="Bearer token for authenticated users"),
) -> AnalyzeDreamResponse:
    """
    Analyze a dream using RAG retrieval and LLM interpretation.
    
    - **user_dream**: The dream narrative to analyze (10-500 characters)
    - **mode**: Analysis mode - 'psychological' for Jungian analysis, 
                'mystical' for esoteric interpretation
    - **Authorization** (Header): Optional Bearer token. If valid, saves dream to DB.
    
    Returns interpretation, Surrealist image prompt, and source documents.
    """
    # Step 1: Check for auth token and verify user (optional)
    user_id: Optional[str] = None
    token = extract_token_from_header(authorization)
    
    if token:
        try:
            user_id = await verify_user_token(token)
            if user_id:
                log_info(f"Analyzing dream for user: {user_id[:8]}...")
            else:
                log_info("Analyzing dream for guest (invalid token provided)")
        except Exception as auth_error:
            log_warning(f"Auth verification failed (non-fatal): {auth_error}")
            user_id = None
    else:
        log_info("Analyzing dream for guest (no auth token)")
    
    # Step 2: Perform AI dream analysis
    try:
        result = await analyze_dream_service.analyze_dream(dream_request)
        log_info(f"Analysis successful - mode: {dream_request.mode.value}, user: {user_id[:8] if user_id else 'Guest'}")
    except ValueError as e:
        log_error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except RuntimeError as e:
        log_error(f"LLM service error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Oracle is meditating (Service busy). Please try again.",
        )
    except Exception as e:
        log_error(f"Unexpected error during analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Oracle is meditating (Service busy). Please try again.",
        )
    
    # Step 3: Save to database if user is authenticated
    if user_id:
        try:
            analysis_data = {
                "interpretation": result.interpretation,
                "image_prompt": result.image_prompt,
                "mode": result.mode.value,
                "sources": [
                    {
                        "source_type": s.source_type,
                        "title": s.title,
                        "relevance_score": s.relevance_score,
                    }
                    for s in result.sources
                ],
            }
            
            dream_id = await save_dream_to_db(
                user_id=user_id,
                content=dream_request.user_dream,
                analysis_data=analysis_data,
            )
            
            if dream_id:
                log_info(f"Dream saved to DB - user: {user_id[:8]}..., id: {dream_id}")
            else:
                log_warning(f"Dream not saved - DB returned None for user: {user_id[:8]}...")
                
        except Exception as db_error:
            log_error(f"Failed to save dream to DB: {db_error}")
    
    # Step 4: Return the analysis result
    return result


# =============================================================================
# Analysis Triangle Endpoint (NEW)
# =============================================================================

class TriangleRequest(BaseModel):
    """Request model for Analysis Triangle."""
    user_dream: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="The dream narrative to analyze"
    )


@router.post(
    "/triangle",
    response_model=TriangleAnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    summary="Analyze dream with Analysis Triangle (Psychology + Tarot + I Ching)",
    description="""
Analyze a dream through three lenses:
1. **Psychology**: Jungian/Freudian subconscious analysis (Vietnamese)
2. **Tarot**: Western mysticism card reading (Vietnamese)
3. **I Ching**: Eastern philosophy hexagram wisdom (Vietnamese)

Also generates a Surrealist art prompt for image generation (English).

**Security**: Requires X-API-Key header.
**Rate Limited**: 5 requests per minute per IP.
    """,
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(f"{settings.rate_limit_requests}/{settings.rate_limit_window}")
async def analyze_dream_triangle(
    triangle_request: TriangleRequest,
    request: Request,  # Required for slowapi
) -> TriangleAnalysisResponse:
    """
    Analyze a dream using the Analysis Triangle architecture.
    
    Returns structured analysis from three perspectives plus an art prompt.
    """
    log_info(f"Triangle analysis request received ({len(triangle_request.user_dream)} chars)")
    
    try:
        result = await analysis_triangle_service.analyze_dream_triangle(
            triangle_request.user_dream
        )
        log_info(f"Triangle analysis complete (id: {result.id[:8]}...)")
        return result
        
    except ValueError as e:
        log_error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        log_error(f"Triangle analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Oracle is meditating. Please try again.",
        )


# =============================================================================
# Tiered Analysis Triangle Endpoint (MONETIZATION)
# =============================================================================

def mask_content_for_tier(
    full_analysis: TriangleAnalysisResponse,
    user_tier: UserTier,
    remaining_quota: int
) -> TieredTriangleResponse:
    """
    Mask premium content for non-Master users.
    
    - Guest/Member: Only see psychology (full access)
    - Master: See everything
    """
    locked = LockedContent()
    
    is_master = user_tier == UserTier.MASTER
    
    # Extract lucky_numbers from synthesis
    analysis_dict = full_analysis.analysis.model_dump()
    lucky_numbers = analysis_dict.get("synthesis", {}).get("numbers", [])
    
    return TieredTriangleResponse(
        id=full_analysis.id,
        user_dream=full_analysis.user_dream,
        user_tier=user_tier,
        remaining_quota=remaining_quota if remaining_quota >= 0 else None,
        
        # Psychology: Always visible
        psychology=analysis_dict.get("psychology", {}),
        
        # Premium content: Masked for non-Master
        tarot=analysis_dict.get("tarot", {}) if is_master else locked,
        iching=analysis_dict.get("iching", {}) if is_master else locked,
        synthesis=analysis_dict.get("synthesis", {}) if is_master else locked,
        lucky_numbers=lucky_numbers if is_master else locked,
        
        # Metadata
        sources=full_analysis.sources,
        created_at=full_analysis.created_at.isoformat(),
    )


@router.post(
    "/triangle-tiered",
    response_model=TieredTriangleResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        402: {"model": ErrorResponse, "description": "Quota exceeded - upgrade required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    summary="Analyze dream with tier-based access (Guest/Member/Master)",
    description="""
Analyze a dream through three lenses with tier-based content access:

**Tier Access:**
- **Guest (no login)**: 1 request/day, Psychology only
- **Member (logged in)**: 3 requests/day, Psychology only
- **Master (premium)**: Unlimited, Full access (Tarot/I Ching/Numbers)

**Content Masking:**
Non-Master users will receive locked placeholders for premium content.

**Security**: Requires X-API-Key header.
**Rate Limited**: 5 requests per minute per IP.
    """,
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(f"{settings.rate_limit_requests}/{settings.rate_limit_window}")
async def analyze_dream_triangle_tiered(
    triangle_request: TriangleRequest,
    request: Request,
    authorization: Optional[str] = Header(None, description="Bearer token for authenticated users"),
) -> TieredTriangleResponse:
    """
    Tiered triangle analysis with quota management and content masking.
    """
    client_ip = get_remote_address(request)
    log_info(f"Tiered triangle request from IP: {client_ip[:8]}...")
    
    # Step 1: Identify user tier
    user_id: Optional[str] = None
    user_tier = UserTier.GUEST
    remaining_quota = 0
    
    token = extract_token_from_header(authorization)
    if token:
        user_id = await verify_user_token(token)
        if user_id:
            # Get user profile to determine tier
            profile = await get_user_profile(user_id)
            if profile:
                db_tier = profile.get("tier", "free")
                user_tier = UserTier.MASTER if db_tier == "master" else UserTier.MEMBER
            else:
                user_tier = UserTier.MEMBER  # New user, default to Member
    
    log_info(f"User tier: {user_tier.value}, user_id: {user_id[:8] if user_id else 'guest'}...")
    
    # Step 2: Check quota
    quota_allowed = False
    
    if user_tier == UserTier.MASTER:
        quota_allowed = True
        remaining_quota = -1  # Unlimited
        
    elif user_tier == UserTier.MEMBER:
        quota_allowed, remaining_quota = await check_member_quota(user_id)
        
    else:  # GUEST
        quota_allowed, remaining_quota = await check_guest_quota(client_ip)
    
    if not quota_allowed:
        tier_name = "Cao Thủ" if user_tier == UserTier.MEMBER else "Member"
        log_warning(f"Quota exceeded for {user_tier.value}: {user_id or client_ip}")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Đã hết lượt sử dụng hôm nay",
                "message": f"Nâng cấp lên {tier_name} để có thêm lượt giải mã",
                "tier": user_tier.value,
                "upgrade_url": "/pricing"
            }
        )
    
    # Step 3: Execute analysis (always full, masking happens later)
    try:
        full_result = await analysis_triangle_service.analyze_dream_triangle(
            triangle_request.user_dream
        )
        log_info(f"Triangle analysis complete (id: {full_result.id[:8]}...)")
        
    except ValueError as e:
        log_error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        log_error(f"Triangle analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Oracle is meditating. Please try again.",
        )
    
    # Step 4: Post-analysis actions (save history, increment usage)
    if user_tier in [UserTier.MEMBER, UserTier.MASTER] and user_id:
        try:
            # Save to history
            await save_dream_to_db(
                user_id=user_id,
                content=triangle_request.user_dream,
                analysis_data=full_result.analysis.model_dump()
            )
            
            # Increment usage for Member (not Master - unlimited)
            if user_tier == UserTier.MEMBER:
                await increment_member_usage(user_id)
                
        except Exception as db_error:
            log_warning(f"Post-analysis DB error (non-fatal): {db_error}")
    
    # Step 5: Mask content and return
    tiered_response = mask_content_for_tier(full_result, user_tier, remaining_quota)
    
    return tiered_response

@router.get(
    "/history",
    summary="Get user's dream history",
    description="Fetch the authenticated user's dream analysis history. Requires valid JWT token.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    dependencies=[Depends(verify_api_key)],
)
async def get_dream_history(
    authorization: Optional[str] = Header(None, description="Bearer token (required)"),
    limit: int = 10,
) -> list:
    """
    Get the authenticated user's dream analysis history.
    
    - **Authorization** (Header): Required Bearer token from Supabase Auth
    - **limit**: Maximum number of dreams to return (default: 10)
    
    Returns list of dreams with content and analysis data.
    """
    # Step 1: Validate authorization header
    if not authorization:
        log_warning("History request blocked - no auth header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required. Please provide Authorization header.",
        )
    
    # Step 2: Extract and verify token
    token = extract_token_from_header(authorization)
    
    if not token:
        log_warning("History request blocked - invalid auth format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use: Bearer <token>",
        )
    
    try:
        user_id = await verify_user_token(token)
    except Exception as e:
        log_error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Oracle is meditating (Service busy). Please try again.",
        )
    
    if not user_id:
        log_warning("History request blocked - invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please login again.",
        )
    
    # Step 3: Fetch dream history from database
    log_info(f"Fetching history for user: {user_id[:8]}... (limit: {limit})")
    
    try:
        history = await get_user_dreams(user_id, limit=limit)
        log_info(f"History fetched - {len(history)} dreams for user: {user_id[:8]}...")
        return history
    except Exception as e:
        log_error(f"Failed to fetch dream history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Oracle is meditating (Service busy). Please try again.",
        )
