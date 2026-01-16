"""
Admin Router
Protected endpoints for scheduled tasks and maintenance operations.
Designed to work with external cron services (cron-job.org, GitHub Actions)
as a fallback for Supabase Free tier where pg_cron may be unavailable.
"""

from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

from config import get_settings
from utils.logger import log_info, log_warning, log_error

settings = get_settings()
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/cron/reset-usage",
    summary="Reset daily usage counters",
    description="""
Manually trigger the daily usage reset for all users and cleanup old dreams.

**Security**: Requires X-Cron-Secret header matching CRON_SECRET env variable.

**Use Case**: Call this endpoint from an external cron service (cron-job.org, 
GitHub Actions) at midnight UTC if Supabase pg_cron is unavailable on Free tier.

**Actions Performed**:
1. Reset `daily_usage` to 0 for all profiles
2. Delete guest_usage records from previous days
3. Delete dreams older than 30 days
    """,
    responses={
        200: {"description": "Reset completed successfully"},
        403: {"description": "Invalid cron secret"},
    }
)
async def manual_reset_usage(
    x_cron_secret: Optional[str] = Header(None, alias="X-Cron-Secret")
):
    """
    Manually trigger daily usage reset.
    Protected by CRON_SECRET env variable.
    """
    # Verify cron secret
    if not settings.cron_secret:
        log_warning("CRON_SECRET not configured - endpoint disabled")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cron endpoint not configured"
        )
    
    if x_cron_secret != settings.cron_secret:
        log_warning("Invalid cron secret provided")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid cron secret"
        )
    
    log_info("Manual cron reset triggered via admin endpoint")
    
    try:
        # Import here to avoid circular imports
        from services.db_service import execute_cron_reset
        
        result = await execute_cron_reset()
        
        log_info(f"Cron reset completed: {result}")
        return {
            "status": "ok",
            "message": "Daily reset and cleanup completed",
            "details": result
        }
        
    except Exception as e:
        log_error(f"Cron reset failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="Admin health check",
    description="Simple health check for monitoring services."
)
async def admin_health():
    """Basic health check for admin endpoints."""
    return {"status": "ok", "endpoint": "admin"}
