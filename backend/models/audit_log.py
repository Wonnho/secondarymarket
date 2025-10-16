"""
Audit Log Model
SQLAlchemy model for audit_logs table
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database import Base


class AuditLog(Base):
    """
    Audit Log model for tracking admin actions

    Attributes:
        id: Primary key
        timestamp: When the action occurred
        admin_id: ID of the admin who performed the action
        admin_name: Name of the admin
        action: Type of action performed
        target: Target of the action (e.g., user_id)
        details: Additional details about the action
        ip_address: IP address of the admin
        user_agent: User agent string
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    admin_id = Column(String(100), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    admin_name = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False, index=True)
    target = Column(String(100), index=True)
    details = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(Text)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, admin='{self.admin_id}', action='{self.action}', target='{self.target}')>"

    def to_dict(self):
        """
        Convert model to dictionary

        Returns:
            dict: Audit log data as dictionary
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'admin_id': self.admin_id,
            'admin_name': self.admin_name,
            'action': self.action,
            'target': self.target,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
