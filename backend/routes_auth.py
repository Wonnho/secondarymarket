"""
Authentication Routes
Login, register, logout endpoints with Redis session management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import User
from schemas import LoginRequest, LoginResponse, UserCreate, UserResponse
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_client_ip
)
import session_manager

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
    ip_address: str = Depends(get_client_ip)
):
    """User login - returns JWT token"""
    # Find user by user_id or email
    user = db.query(User).filter(
        (User.user_id == credentials.user_id) |
        (User.email == credentials.user_id)
    ).first()

    # Verify credentials
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create token
    access_token = create_access_token(
        data={"sub": user.user_id, "role": user.role},
        expires_delta=timedelta(minutes=60)
    )

    # Create Redis session
    session_created = session_manager.create_session(
        token=access_token,
        user_data={
            "user_id": user.user_id,
            "user_name": user.name,
            "email": user.email,
            "role": user.role,
            "ip_address": ip_address
        }
    )

    if not session_created:
        print(f"⚠️  Warning: Failed to create Redis session for user {user.user_id}")

    return LoginResponse(
        user_id=user.user_id,
        user_name=user.name,
        email=user.email,
        role=user.role,
        access_token=access_token,
        token_type="bearer",
        expires_in=3600
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """User registration"""
    # Check if user_id exists
    if db.query(User).filter(User.user_id == user_data.user_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID already registered"
        )

    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    new_user = User(
        user_id=user_data.user_id,
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role.value,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    """
    Logout - removes session from Redis

    Args:
        authorization: Bearer token from Authorization header
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"message": "No active session to logout"}

    # Extract token from "Bearer <token>"
    token = authorization.replace("Bearer ", "")

    # Delete Redis session
    session_deleted = session_manager.delete_session(token)

    if session_deleted:
        return {"message": "Successfully logged out"}
    else:
        return {"message": "Session already expired or not found"}
