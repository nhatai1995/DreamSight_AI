"""
Database Service
Supabase integration for authentication and data persistence.
Handles JWT verification and dream storage in PostgreSQL.
"""

from typing import Optional, Any
import json

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

from config import get_settings

settings = get_settings()

# Global Supabase client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Get or create the Supabase client instance.
    Returns None if Supabase is not configured.
    """
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    if not settings.supabase_url or not settings.supabase_key:
        print("⚠️ Supabase not configured (SUPABASE_URL or SUPABASE_KEY missing)")
        return None
    
    try:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            )
        )
        print("✓ Supabase client initialized")
        return _supabase_client
    except Exception as e:
        print(f"✗ Failed to initialize Supabase client: {e}")
        return None


async def verify_user_token(token: str) -> Optional[str]:
    """
    Verify a JWT token from the frontend and return the user_id.
    
    Args:
        token: The JWT token from Authorization header (without 'Bearer ')
        
    Returns:
        The user_id (UUID string) if valid, None otherwise
    """
    client = get_supabase_client()
    
    if client is None:
        print("⚠️ Cannot verify token: Supabase not configured")
        return None
    
    try:
        # Use Supabase Auth to validate the token
        response = client.auth.get_user(token)
        
        if response and response.user:
            user_id = str(response.user.id)
            print(f"✓ Token verified for user: {user_id[:8]}...")
            return user_id
        else:
            print("✗ Token verification failed: No user returned")
            return None
            
    except Exception as e:
        # Token invalid, expired, or other auth error
        print(f"✗ Token verification error: {e}")
        return None


async def save_dream_to_db(
    user_id: str,
    content: str,
    analysis_data: dict[str, Any]
) -> Optional[int]:
    """
    Save a dream and its analysis to the Supabase database.
    
    Args:
        user_id: The authenticated user's UUID
        content: The original dream text
        analysis_data: The AI analysis result (will be stored as JSONB)
        
    Returns:
        The dream record ID if successful, None otherwise
    """
    client = get_supabase_client()
    
    if client is None:
        print("⚠️ Cannot save dream: Supabase not configured")
        return None
    
    try:
        # Prepare the data for insertion
        dream_record = {
            "user_id": user_id,
            "content": content,
            "analysis": analysis_data,
        }
        
        # Insert into dreams table
        response = client.table("dreams").insert(dream_record).execute()
        
        if response.data and len(response.data) > 0:
            dream_id = response.data[0].get("id")
            print(f"✓ Dream saved to database (id: {dream_id})")
            return dream_id
        else:
            print("⚠️ Dream insert returned no data")
            return None
            
    except Exception as e:
        # Log error but don't crash - saving is optional
        print(f"✗ Failed to save dream to database: {e}")
        return None


async def get_user_dreams(user_id: str, limit: int = 10) -> list[dict]:
    """
    Get recent dreams for a user.
    
    Args:
        user_id: The user's UUID
        limit: Maximum number of dreams to return
        
    Returns:
        List of dream records
    """
    client = get_supabase_client()
    
    if client is None:
        return []
    
    try:
        response = (
            client.table("dreams")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        
        return response.data if response.data else []
        
    except Exception as e:
        print(f"✗ Failed to fetch user dreams: {e}")
        return []


# =============================================================================
# Tiered Quota Management Functions
# =============================================================================

async def get_user_profile(user_id: str) -> Optional[dict]:
    """
    Get user profile including tier and daily usage.
    
    Args:
        user_id: The user's UUID
        
    Returns:
        Profile dict with tier, daily_usage, last_reset_date, or None
    """
    client = get_supabase_client()
    
    if client is None:
        return None
    
    try:
        response = (
            client.table("profiles")
            .select("tier, daily_usage, last_reset_date")
            .eq("id", user_id)
            .single()
            .execute()
        )
        
        return response.data if response.data else None
        
    except Exception as e:
        print(f"✗ Failed to fetch user profile: {e}")
        return None


async def check_guest_quota(ip_address: str) -> tuple[bool, int]:
    """
    Check and consume guest quota using IP-based tracking.
    
    Args:
        ip_address: Client IP address
        
    Returns:
        Tuple of (is_allowed, remaining_quota)
    """
    client = get_supabase_client()
    
    if client is None:
        # If Supabase not configured, allow as fallback
        return True, 0
    
    try:
        # Call the PostgreSQL function we created
        response = client.rpc("check_guest_quota", {"guest_ip": ip_address}).execute()
        
        is_allowed = response.data if response.data is not None else False
        remaining = 0 if is_allowed else 0  # Guest only gets 1, so 0 remaining after use
        
        return is_allowed, remaining
        
    except Exception as e:
        print(f"✗ Guest quota check failed: {e}")
        # On error, allow the request but log
        return True, 0


async def check_member_quota(user_id: str) -> tuple[bool, int]:
    """
    Check if member has remaining quota for today.
    
    Args:
        user_id: The user's UUID
        
    Returns:
        Tuple of (is_allowed, remaining_quota)
    """
    profile = await get_user_profile(user_id)
    
    if profile is None:
        # No profile found, treat as new user with fresh quota
        return True, 2  # 3 total - 1 = 2 remaining
    
    daily_usage = profile.get("daily_usage", 0)
    tier = profile.get("tier", "free")
    
    # Master tier has unlimited
    if tier == "master":
        return True, -1  # -1 indicates unlimited
    
    # Member tier: 3 requests per day
    member_limit = 3
    remaining = member_limit - daily_usage
    
    if remaining > 0:
        return True, remaining - 1  # Will be this many after current request
    else:
        return False, 0


async def increment_member_usage(user_id: str) -> bool:
    """
    Increment daily usage counter for a member.
    
    Args:
        user_id: The user's UUID
        
    Returns:
        True if successful
    """
    client = get_supabase_client()
    
    if client is None:
        return False
    
    try:
        # Increment daily_usage by 1
        response = (
            client.table("profiles")
            .update({"daily_usage": client.table("profiles").select("daily_usage").eq("id", user_id).single().execute().data.get("daily_usage", 0) + 1})
            .eq("id", user_id)
            .execute()
        )
        
        # Simpler approach using RPC would be better, but this works
        # Actually let's use raw SQL increment
        client.rpc("increment_daily_usage", {"p_user_id": user_id}).execute()
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to increment usage: {e}")
        # Try direct update as fallback
        try:
            profile = await get_user_profile(user_id)
            new_usage = (profile.get("daily_usage", 0) + 1) if profile else 1
            client.table("profiles").update({"daily_usage": new_usage}).eq("id", user_id).execute()
            return True
        except:
            return False


async def execute_cron_reset() -> dict:
    """
    Execute the daily cron reset operations.
    Called by admin endpoint for external cron services.
    
    Returns:
        Dict with operation results
    """
    client = get_supabase_client()
    
    if client is None:
        return {"error": "Supabase not configured"}
    
    results = {
        "profiles_reset": 0,
        "guests_cleaned": 0,
        "old_dreams_deleted": 0,
    }
    
    try:
        # 1. Reset daily_usage for all profiles
        reset_response = (
            client.table("profiles")
            .update({"daily_usage": 0})
            .neq("daily_usage", 0)  # Only update those with usage > 0
            .execute()
        )
        results["profiles_reset"] = len(reset_response.data) if reset_response.data else 0
        
    except Exception as e:
        print(f"✗ Profile reset failed: {e}")
        results["profiles_error"] = str(e)
    
    try:
        # 2. Clean old guest usage records
        from datetime import date
        today = date.today().isoformat()
        
        guest_response = (
            client.table("guest_usage")
            .delete()
            .lt("usage_date", today)
            .execute()
        )
        results["guests_cleaned"] = len(guest_response.data) if guest_response.data else 0
        
    except Exception as e:
        print(f"✗ Guest cleanup failed: {e}")
        results["guests_error"] = str(e)
    
    try:
        # 3. Delete dreams older than 30 days
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        dreams_response = (
            client.table("dreams")
            .delete()
            .lt("created_at", cutoff)
            .execute()
        )
        results["old_dreams_deleted"] = len(dreams_response.data) if dreams_response.data else 0
        
    except Exception as e:
        print(f"✗ Dreams cleanup failed: {e}")
        results["dreams_error"] = str(e)
    
    print(f"✓ Cron reset completed: {results}")
    return results
