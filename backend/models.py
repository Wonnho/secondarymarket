"""
Database Models
All SQLAlchemy ORM models in one file
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from backend.database import Base


class User(Base):
    """User model for authentication and user management"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='user', nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin', 'super_admin')", name='valid_role'),
    )

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', email='{self.email}', role='{self.role}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def is_admin_role(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in ['admin', 'super_admin']

    def is_super_admin_role(self) -> bool:
        """Check if user is super admin"""
        return self.role == 'super_admin'

    def can_manage_user(self, target_user_role: str) -> bool:
        """Check if can manage another user based on roles"""
        if self.role == 'super_admin':
            return True
        if self.role == 'admin':
            return target_user_role == 'user'
        return False


class AuditLog(Base):
    """Audit log model for tracking admin actions"""

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
        return f"<AuditLog(id={self.id}, admin='{self.admin_id}', action='{self.action}')>"

    def to_dict(self):
        """Convert to dictionary"""
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
