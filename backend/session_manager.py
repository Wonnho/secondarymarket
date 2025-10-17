"""
Redis-based Session Management
Handles JWT token storage and session lifecycle in Redis
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from redis_client import (
    set_value,
    get_value,
    delete_value,
    exists,
    get_ttl,
    extend_expiry,
    get_keys_by_pattern,
    delete_by_pattern
)


# Session configuration
SESSION_PREFIX = "session"
SESSION_EXPIRY = 3600  # 1 hour in seconds
REFRESH_THRESHOLD = 900  # Refresh if less than 15 minutes remaining


def _get_session_key(token: str) -> str:
    """
    Generate Redis key for session

    Args:
        token: JWT access token

    Returns:
        str: Redis key (e.g., "session:eyJhbGc...")
    """
    return f"{SESSION_PREFIX}:{token}"


def create_session(token: str, user_data: Dict[str, Any], expire: int = SESSION_EXPIRY) -> bool:
    """
    Create a new session in Redis

    Args:
        token: JWT access token
        user_data: User information to store
            - user_id: str
            - user_name: str
            - email: str
            - role: str
        expire: Session expiration in seconds (default: 1 hour)

    Returns:
        bool: True if session created successfully
    """
    try:
        session_key = _get_session_key(token)

        session_data = {
            **user_data,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "token": token
        }

        success = set_value(session_key, session_data, expire)

        if success:
            print(f"✅ Session created for user: {user_data.get('user_id')}")
        else:
            print(f"❌ Failed to create session for user: {user_data.get('user_id')}")

        return success

    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return False


def get_session(token: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve session data from Redis

    Args:
        token: JWT access token

    Returns:
        dict: Session data or None if not found/expired
    """
    try:
        session_key = _get_session_key(token)
        session_data = get_value(session_key, deserialize=True)

        if session_data:
            # Update last activity timestamp
            session_data["last_activity"] = datetime.utcnow().isoformat()
            set_value(session_key, session_data, get_ttl(session_key))

            # Auto-refresh session if close to expiry
            ttl = get_ttl(session_key)
            if 0 < ttl < REFRESH_THRESHOLD:
                extend_expiry(session_key, SESSION_EXPIRY - ttl)
                print(f"🔄 Session auto-refreshed for user: {session_data.get('user_id')}")

        return session_data

    except Exception as e:
        print(f"❌ Error getting session: {e}")
        return None


def update_session(token: str, update_data: Dict[str, Any]) -> bool:
    """
    Update session data in Redis

    Args:
        token: JWT access token
        update_data: Data to update in session

    Returns:
        bool: True if updated successfully
    """
    try:
        session_key = _get_session_key(token)
        session_data = get_value(session_key, deserialize=True)

        if not session_data:
            print(f"❌ Session not found for token: {token[:20]}...")
            return False

        # Merge update data
        session_data.update(update_data)
        session_data["last_activity"] = datetime.utcnow().isoformat()

        # Preserve TTL
        ttl = get_ttl(session_key)
        success = set_value(session_key, session_data, ttl if ttl > 0 else SESSION_EXPIRY)

        if success:
            print(f"✅ Session updated for user: {session_data.get('user_id')}")

        return success

    except Exception as e:
        print(f"❌ Error updating session: {e}")
        return False


def delete_session(token: str) -> bool:
    """
    Delete session from Redis (logout)

    Args:
        token: JWT access token

    Returns:
        bool: True if deleted successfully
    """
    try:
        session_key = _get_session_key(token)
        session_data = get_value(session_key, deserialize=True)

        success = delete_value(session_key)

        if success and session_data:
            print(f"✅ Session deleted for user: {session_data.get('user_id')}")
        elif not session_data:
            print(f"⚠️  Session not found (may be already expired)")
            success = True  # Consider it success if session doesn't exist

        return success

    except Exception as e:
        print(f"❌ Error deleting session: {e}")
        return False


def session_exists(token: str) -> bool:
    """
    Check if session exists in Redis

    Args:
        token: JWT access token

    Returns:
        bool: True if session exists
    """
    try:
        session_key = _get_session_key(token)
        return exists(session_key)
    except Exception as e:
        print(f"❌ Error checking session existence: {e}")
        return False


def refresh_session(token: str, new_expiry: Optional[int] = None) -> bool:
    """
    Refresh session expiration time

    Args:
        token: JWT access token
        new_expiry: New expiration in seconds (default: SESSION_EXPIRY)

    Returns:
        bool: True if refreshed successfully
    """
    try:
        session_key = _get_session_key(token)

        if not exists(session_key):
            print(f"❌ Cannot refresh: session not found")
            return False

        session_data = get_value(session_key, deserialize=True)
        if not session_data:
            return False

        session_data["last_activity"] = datetime.utcnow().isoformat()

        expiry = new_expiry if new_expiry else SESSION_EXPIRY
        success = set_value(session_key, session_data, expiry)

        if success:
            print(f"✅ Session refreshed for user: {session_data.get('user_id')}")

        return success

    except Exception as e:
        print(f"❌ Error refreshing session: {e}")
        return False


def get_user_sessions(user_id: str) -> list:
    """
    Get all active sessions for a user

    Args:
        user_id: User ID

    Returns:
        list: List of session data dictionaries
    """
    try:
        pattern = f"{SESSION_PREFIX}:*"
        all_keys = get_keys_by_pattern(pattern)

        user_sessions = []
        for key in all_keys:
            session_data = get_value(key, deserialize=True)
            if session_data and session_data.get("user_id") == user_id:
                user_sessions.append({
                    **session_data,
                    "ttl": get_ttl(key)
                })

        return user_sessions

    except Exception as e:
        print(f"❌ Error getting user sessions: {e}")
        return []


def delete_user_sessions(user_id: str) -> int:
    """
    Delete all sessions for a specific user

    Args:
        user_id: User ID

    Returns:
        int: Number of sessions deleted
    """
    try:
        user_sessions = get_user_sessions(user_id)
        deleted_count = 0

        for session in user_sessions:
            if delete_session(session.get("token")):
                deleted_count += 1

        print(f"✅ Deleted {deleted_count} sessions for user: {user_id}")
        return deleted_count

    except Exception as e:
        print(f"❌ Error deleting user sessions: {e}")
        return 0


def get_all_sessions() -> list:
    """
    Get all active sessions (admin only)

    Returns:
        list: List of all session data
    """
    try:
        pattern = f"{SESSION_PREFIX}:*"
        all_keys = get_keys_by_pattern(pattern)

        all_sessions = []
        for key in all_keys:
            session_data = get_value(key, deserialize=True)
            if session_data:
                all_sessions.append({
                    **session_data,
                    "ttl": get_ttl(key)
                })

        return all_sessions

    except Exception as e:
        print(f"❌ Error getting all sessions: {e}")
        return []


def cleanup_expired_sessions() -> int:
    """
    Cleanup expired sessions (Redis handles this automatically,
    but this can be used for manual cleanup)

    Returns:
        int: Number of sessions cleaned up
    """
    try:
        pattern = f"{SESSION_PREFIX}:*"
        all_keys = get_keys_by_pattern(pattern)

        cleaned_count = 0
        for key in all_keys:
            ttl = get_ttl(key)
            if ttl == -2:  # Key doesn't exist (already expired)
                cleaned_count += 1

        print(f"✅ Cleaned up {cleaned_count} expired sessions")
        return cleaned_count

    except Exception as e:
        print(f"❌ Error cleaning up sessions: {e}")
        return 0


def get_session_stats() -> Dict[str, Any]:
    """
    Get session statistics

    Returns:
        dict: Session statistics
    """
    try:
        all_sessions = get_all_sessions()

        stats = {
            "total_sessions": len(all_sessions),
            "sessions_by_role": {},
            "average_ttl": 0
        }

        if all_sessions:
            ttl_sum = 0
            for session in all_sessions:
                role = session.get("role", "unknown")
                stats["sessions_by_role"][role] = stats["sessions_by_role"].get(role, 0) + 1
                ttl_sum += session.get("ttl", 0)

            stats["average_ttl"] = ttl_sum // len(all_sessions)

        return stats

    except Exception as e:
        print(f"❌ Error getting session stats: {e}")
        return {"error": str(e)}
