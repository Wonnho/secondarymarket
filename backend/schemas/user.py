"""
User Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserBase(BaseModel):
    """Base user schema with common fields"""
    user_id: str = Field(..., min_length=3, max_length=100, description="Unique user ID")
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User full name")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=6, max_length=100, description="User password")
    role: UserRole = Field(default=UserRole.USER, description="User role")

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, max_length=100, description="New password")

    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserResponse(UserBase):
    """Schema for user response (full info for admin)"""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserPublicResponse(BaseModel):
    """Schema for public user info (limited fields)"""
    user_id: str
    name: str
    role: str

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for list of users with pagination"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserSearchQuery(BaseModel):
    """Schema for user search query parameters"""
    search: Optional[str] = Field(None, description="Search by user_id, email, or name")
    role: Optional[UserRole] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")


class LoginRequest(BaseModel):
    """Schema for login request"""
    user_id: str = Field(..., description="User ID or email")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Schema for login response"""
    user_id: str
    user_name: str
    email: str
    role: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds


class TokenData(BaseModel):
    """Schema for JWT token data"""
    user_id: str
    role: str
    exp: Optional[datetime] = None
