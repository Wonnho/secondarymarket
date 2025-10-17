"""
Session Management Routes
Admin endpoints for managing user sessions in Redis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel

from auth import require_admin, get_current_user
from models import User
import session_manager


router = APIRouter(prefix="/session", tags=["Session Management"])


# Response schemas
class SessionInfo(BaseModel):
    """Single session information"""
    user_id: str
    user_name: str
    email: str
    role: str
    created_at: str
    last_activity: str
    ttl: int
    ip_address: str = None


class SessionStats(BaseModel):
    """Session statistics"""
    total_sessions: int
    sessions_by_role: Dict[str, int]
    average_ttl: int


class SessionListResponse(BaseModel):
    """List of sessions response"""
    sessions: List[Dict[str, Any]]
    total: int


# ==================== User Session Endpoints ====================

@router.get("/me", response_model=SessionInfo)
def get_my_session(current_user: User = Depends(get_current_user)):
    """
    Get current user's session information

    Returns:
        SessionInfo: Current session details
    """
    # Note: In real implementation, we need to pass the token
    # For now, we'll get all user sessions and return the first one
    user_sessions = session_manager.get_user_sessions(current_user.user_id)

    if not user_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )

    session_data = user_sessions[0]  # Get most recent session
    return SessionInfo(**session_data)


@router.post("/refresh")
def refresh_my_session(current_user: User = Depends(get_current_user)):
    """
    Refresh current user's session (extend TTL)

    Returns:
        dict: Success message
    """
    user_sessions = session_manager.get_user_sessions(current_user.user_id)

    if not user_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )

    token = user_sessions[0].get("token")
    refreshed = session_manager.refresh_session(token)

    if refreshed:
        return {"message": "Session refreshed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh session"
        )


# ==================== Admin Session Endpoints ====================

@router.get("/all", response_model=SessionListResponse, dependencies=[Depends(require_admin)])
def get_all_sessions():
    """
    Get all active sessions (Admin only)

    Returns:
        SessionListResponse: List of all active sessions
    """
    all_sessions = session_manager.get_all_sessions()

    return SessionListResponse(
        sessions=all_sessions,
        total=len(all_sessions)
    )


@router.get("/stats", response_model=SessionStats, dependencies=[Depends(require_admin)])
def get_session_statistics():
    """
    Get session statistics (Admin only)

    Returns:
        SessionStats: Session statistics
    """
    stats = session_manager.get_session_stats()

    return SessionStats(
        total_sessions=stats.get("total_sessions", 0),
        sessions_by_role=stats.get("sessions_by_role", {}),
        average_ttl=stats.get("average_ttl", 0)
    )


@router.get("/user/{user_id}", response_model=SessionListResponse, dependencies=[Depends(require_admin)])
def get_user_sessions_admin(user_id: str):
    """
    Get all sessions for a specific user (Admin only)

    Args:
        user_id: User ID to query

    Returns:
        SessionListResponse: List of user's active sessions
    """
    user_sessions = session_manager.get_user_sessions(user_id)

    if not user_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active sessions found for user: {user_id}"
        )

    return SessionListResponse(
        sessions=user_sessions,
        total=len(user_sessions)
    )


@router.delete("/user/{user_id}", dependencies=[Depends(require_admin)])
def delete_user_sessions_admin(user_id: str):
    """
    Delete all sessions for a specific user (Admin only)

    This will log out the user from all devices

    Args:
        user_id: User ID

    Returns:
        dict: Number of sessions deleted
    """
    deleted_count = session_manager.delete_user_sessions(user_id)

    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active sessions found for user: {user_id}"
        )

    return {
        "message": f"Successfully deleted {deleted_count} session(s) for user {user_id}",
        "deleted_count": deleted_count
    }


@router.post("/cleanup", dependencies=[Depends(require_admin)])
def cleanup_expired_sessions_admin():
    """
    Manually cleanup expired sessions (Admin only)

    Note: Redis automatically removes expired keys,
    but this endpoint can be used for manual cleanup

    Returns:
        dict: Cleanup results
    """
    cleaned_count = session_manager.cleanup_expired_sessions()

    return {
        "message": f"Cleanup completed",
        "cleaned_sessions": cleaned_count
    }
