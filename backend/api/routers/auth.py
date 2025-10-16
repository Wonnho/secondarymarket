"""
Authentication Router
API endpoints for user authentication (login, register, etc.)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.core.database import get_db
from backend.models.user import User
from backend.schemas.user import LoginRequest, LoginResponse, UserCreate, UserResponse
from backend.utils.auth import verify_password, get_password_hash, create_access_token
from backend.api.dependencies import get_current_user, get_client_ip, get_user_agent

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
    ip_address: str = Depends(get_client_ip)
):
    """
    User login endpoint

    Args:
        credentials: Login credentials (user_id and password)
        db: Database session
        ip_address: Client IP address

    Returns:
        LoginResponse: User info and access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by user_id or email
    user = db.query(User).filter(
        (User.user_id == credentials.user_id) |
        (User.email == credentials.user_id)
    ).first()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive. Please contact administrator."
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.user_id, "role": user.role},
        expires_delta=access_token_expires
    )

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
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    User registration endpoint

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: If user_id or email already exists
    """
    # Check if user_id already exists
    existing_user = db.query(User).filter(User.user_id == user_data.user_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        user_id=user_data.user_id,
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        role=user_data.role.value,  # Convert enum to string
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse: Current user info
    """
    return current_user


@router.post("/logout")
def logout():
    """
    User logout endpoint

    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by removing the token. This endpoint is here for consistency.

    Returns:
        dict: Success message
    """
    return {"message": "Successfully logged out"}
