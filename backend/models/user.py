"""
User Model
SQLAlchemy model for users table
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.sql import func
from datetime import datetime
from backend.core.database import Base


class User(Base):
    """
    User model representing the users table in database

    Attributes:
        id: Primary key
        user_id: Unique username/user ID
        email: User's email address
        name: User's full name
        password_hash: Bcrypt hashed password
        role: User role (user, admin, super_admin)
        is_active: Account activation status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp
    """

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

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin', 'super_admin')",
            name='valid_role'
        ),
    )

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', email='{self.email}', role='{self.role}')>"

    def to_dict(self):
        """
        Convert model to dictionary

        Returns:
            dict: User data as dictionary
        """
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

    def to_dict_public(self):
        """
        Convert model to dictionary (public info only, no sensitive data)

        Returns:
            dict: Public user data
        """
        return {
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active
        }

    def is_admin_role(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in ['admin', 'super_admin']

    def is_super_admin_role(self) -> bool:
        """Check if user is super admin"""
        return self.role == 'super_admin'

    def can_manage_user(self, target_user_role: str) -> bool:
        """
        Check if this user can manage another user based on roles

        Args:
            target_user_role: Role of the target user

        Returns:
            bool: True if can manage, False otherwise
        """
        # Super admin can manage everyone
        if self.role == 'super_admin':
            return True

        # Admin can manage regular users only
        if self.role == 'admin':
            return target_user_role == 'user'

        # Regular users cannot manage anyone
        return False
