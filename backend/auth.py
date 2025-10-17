"""
Authentication Module
Password hashing, JWT tokens, and auth dependencies all in one place
"""
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os

from database import get_db
from models import User
import session_manager

# ==================== Configuration ====================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


# ==================== Password Hashing ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


# ==================== JWT Token Management ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ==================== FastAPI Dependencies ====================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token with Redis session validation

    This validates:
    1. JWT token signature and expiration
    2. Redis session existence
    3. User exists in database
    4. User is active
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    session_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session expired, please login again",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Step 1: Validate JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Step 2: Validate Redis session
    session_data = session_manager.get_session(token)
    if session_data is None:
        raise session_expired_exception

    # Step 3: Query user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception

    # Step 4: Check if user is active
    if not user.is_active:
        # Delete session for inactive user
        session_manager.delete_session(token)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin or super_admin role"""
    if not current_user.is_admin_role():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require super_admin role"""
    if not current_user.is_super_admin_role():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_user


# ==================== Helper Functions ====================

def get_client_ip(
    x_forwarded_for: Optional[str] = Header(None),
    x_real_ip: Optional[str] = Header(None)
) -> Optional[str]:
    """Get client IP address from headers"""
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    elif x_real_ip:
        return x_real_ip
    return None


def get_user_agent(user_agent: Optional[str] = Header(None)) -> Optional[str]:
    """Get user agent from headers"""
    return user_agent
