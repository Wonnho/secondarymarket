"""
Audit Log Schemas
Pydantic models for audit log validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AuditLogCreate(BaseModel):
    """Schema for creating audit log entry"""
    admin_id: str = Field(..., description="ID of admin performing action")
    admin_name: str = Field(..., description="Name of admin")
    action: str = Field(..., description="Action performed")
    target: Optional[str] = Field(None, description="Target of action")
    details: Optional[str] = Field(None, description="Additional details")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")


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
