"""
Admin Routes
User management, analytics, and audit log endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from datetime import datetime

from database import get_db
from models import User, AuditLog
from schemas import (
    UserResponse,
    UserListResponse,
    UserUpdate,
    UserRole,
    AuditLogResponse,
    AuditLogListResponse
)
from auth import (
    require_admin,
    require_super_admin,
    get_client_ip,
    get_user_agent,
    get_password_hash
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=UserListResponse)
def get_all_users(
    search: Optional[str] = Query(None, description="Search by user_id, email, or name"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get list of all users with search and filter capabilities

    Args:
        search: Search term for user_id, email, or name
        role: Filter by user role
        is_active: Filter by active status
        page: Page number for pagination
        page_size: Number of items per page
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        UserListResponse: List of users with pagination info
    """
    # Base query
    query = db.query(User)

    # Apply search filter
    if search:
        search_filter = or_(
            User.user_id.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Apply role filter
    if role:
        query = query.filter(User.role == role.value)

    # Apply active status filter
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    # Get users for current page
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    return UserListResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get specific user by user_id

    Args:
        user_id: User ID to retrieve
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        UserResponse: User information

    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    ip_address: str = Depends(get_client_ip)
):
    """
    Update user information

    Args:
        user_id: User ID to update
        user_update: Updated user data
        db: Database session
        current_user: Current authenticated admin user
        ip_address: Client IP address

    Returns:
        UserResponse: Updated user information

    Raises:
        HTTPException: If user not found or permission denied
    """
    # Get user to update
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    # Check permission
    if not current_user.can_manage_user(user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot manage user with role '{user.role}'"
        )

    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "role" and value:
            setattr(user, field, value.value)  # Convert enum to string
        else:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)

    # Log action
    log_entry = AuditLog(
        admin_id=current_user.user_id,
        admin_name=current_user.name,
        action="update_user",
        target=user_id,
        details=f"Updated user: {', '.join(update_data.keys())}",
        ip_address=ip_address
    )
    db.add(log_entry)
    db.commit()

    return user


@router.post("/users/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    ip_address: str = Depends(get_client_ip)
):
    """
    Activate user account

    Args:
        user_id: User ID to activate
        db: Database session
        current_user: Current authenticated admin user
        ip_address: Client IP address

    Returns:
        UserResponse: Updated user information
    """
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    # Check permission
    if not current_user.can_manage_user(user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot manage user with role '{user.role}'"
        )

    user.is_active = True
    db.commit()
    db.refresh(user)

    # Log action
    log_entry = AuditLog(
        admin_id=current_user.user_id,
        admin_name=current_user.name,
        action="activate_user",
        target=user_id,
        details="User account activated",
        ip_address=ip_address
    )
    db.add(log_entry)
    db.commit()

    return user


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    ip_address: str = Depends(get_client_ip)
):
    """
    Deactivate user account

    Args:
        user_id: User ID to deactivate
        db: Database session
        current_user: Current authenticated admin user
        ip_address: Client IP address

    Returns:
        UserResponse: Updated user information
    """
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    # Check permission
    if not current_user.can_manage_user(user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot manage user with role '{user.role}'"
        )

    # Prevent deactivating self
    if user.user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    user.is_active = False
    db.commit()
    db.refresh(user)

    # Log action
    log_entry = AuditLog(
        admin_id=current_user.user_id,
        admin_name=current_user.name,
        action="deactivate_user",
        target=user_id,
        details="User account deactivated",
        ip_address=ip_address
    )
    db.add(log_entry)
    db.commit()

    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    ip_address: str = Depends(get_client_ip)
):
    """
    Delete user account permanently

    Args:
        user_id: User ID to delete
        db: Database session
        current_user: Current authenticated admin user
        ip_address: Client IP address

    Returns:
        dict: Success message

    Raises:
        HTTPException: If user not found or permission denied
    """
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    # Check permission
    if not current_user.can_manage_user(user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot manage user with role '{user.role}'"
        )

    # Prevent deleting self
    if user.user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Log action before deleting
    log_entry = AuditLog(
        admin_id=current_user.user_id,
        admin_name=current_user.name,
        action="delete_user",
        target=user_id,
        details=f"User account deleted permanently",
        ip_address=ip_address
    )
    db.add(log_entry)

    # Delete user
    db.delete(user)
    db.commit()

    return {"message": f"User '{user_id}' deleted successfully"}


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    ip_address: str = Depends(get_client_ip)
):
    """
    Reset user password (admin function)

    Args:
        user_id: User ID for password reset
        db: Database session
        current_user: Current authenticated admin user
        ip_address: Client IP address

    Returns:
        dict: Success message with temporary password

    Note: In production, this should send an email instead of returning password
    """
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    # Check permission
    if not current_user.can_manage_user(user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot manage user with role '{user.role}'"
        )

    # Generate temporary password
    temp_password = f"Temp{user_id}123!"
    user.password_hash = get_password_hash(temp_password)
    db.commit()

    # Log action
    log_entry = AuditLog(
        admin_id=current_user.user_id,
        admin_name=current_user.name,
        action="reset_password",
        target=user_id,
        details="Password reset by admin",
        ip_address=ip_address
    )
    db.add(log_entry)
    db.commit()

    # TODO: In production, send email instead
    return {
        "message": f"Password reset for user '{user_id}'",
        "temporary_password": temp_password,
        "note": "In production, this should be sent via email"
    }


@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    action: Optional[str] = Query(None),
    admin_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get audit logs with pagination and filters

    Args:
        page: Page number
        page_size: Items per page
        action: Filter by action type
        admin_id: Filter by admin ID
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        AuditLogListResponse: List of audit logs
    """
    query = db.query(AuditLog)

    # Apply filters
    if action:
        query = query.filter(AuditLog.action == action)
    if admin_id:
        query = query.filter(AuditLog.admin_id == admin_id)

    # Get total count
    total = query.count()

    # Calculate offset
    offset = (page - 1) * page_size

    # Get logs for current page
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(page_size).all()

    return AuditLogListResponse(
        logs=logs,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/analytics/users")
def get_user_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get user analytics and statistics

    Args:
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        dict: User analytics data
    """
    # Total users
    total_users = db.query(func.count(User.id)).scalar()

    # Active users
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()

    # Users by role
    users_by_role = db.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()

    role_distribution = {role: count for role, count in users_by_role}

    # Recent registrations (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_registrations = db.query(func.count(User.id)).filter(
        User.created_at >= week_ago
    ).scalar()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "role_distribution": role_distribution,
        "recent_registrations_7days": recent_registrations,
        "activity_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
    }
