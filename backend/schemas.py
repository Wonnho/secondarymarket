"""
Pydantic Schemas
All request/response validation schemas in one file
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


# ==================== User Schemas ====================

class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserBase(BaseModel):
    """Base user schema"""
    user_id: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = Field(default=UserRole.USER)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for list of users with pagination"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LoginRequest(BaseModel):
    """Schema for login request"""
    user_id: str
    password: str


class LoginResponse(BaseModel):
    """Schema for login response"""
    user_id: str
    user_name: str
    email: str
    role: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


# ==================== Audit Log Schemas ====================

class AuditLogCreate(BaseModel):
    """Schema for creating audit log"""
    admin_id: str
    admin_name: str
    action: str
    target: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    timestamp: datetime
    admin_id: str
    admin_name: str
    action: str
    target: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for list of audit logs"""
    logs: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
