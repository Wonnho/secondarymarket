# 🛡️ Admin Dashboard Design - User Management

## 📋 Overview

Design document for implementing an admin dashboard to view and manage user registration/account information.

**Date:** 2025-10-16
**Status:** Design Phase

---

## 🎯 Requirements

### Admin Capabilities
1. **View all registered users**
   - List of all users with pagination
   - Search and filter capabilities
   - Sort by registration date, last login, etc.

2. **View user details**
   - User ID, email, name
   - Registration date
   - Last login date
   - Account status (active/inactive)
   - Login history

3. **Manage users**
   - Activate/deactivate accounts
   - Reset passwords
   - Delete users
   - Edit user information

4. **Analytics**
   - Total users count
   - New registrations (today, week, month)
   - Active users
   - Login statistics

---

## 🏗️ Architecture Design

### Option 1: Separate Admin Page (Recommended)

```
secondarymarket/
├── frontend/
│   ├── pages/
│   │   ├── login.py
│   │   ├── signup.py
│   │   ├── admin/                    # ✅ NEW: Admin pages
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py          # Admin dashboard
│   │   │   ├── users.py              # User management
│   │   │   └── analytics.py          # Analytics
│   │   └── ...
│   ├── utils/
│   │   ├── auth.py
│   │   └── admin_auth.py             # ✅ NEW: Admin auth utilities
│   └── ...
```

### Option 2: Integrated Admin Section

```
# Add admin section to main navigation
# Only visible to admin users
```

### Option 3: Separate Admin Application

```
secondarymarket/
├── frontend/          # User-facing app
└── admin_frontend/    # Separate admin app
```

**Recommendation:** Option 1 - Separate admin pages within the same app

---

## 🔐 Role-Based Access Control (RBAC)

### User Roles

```python
class UserRole:
    USER = "user"           # Regular user
    ADMIN = "admin"         # Administrator
    SUPER_ADMIN = "super_admin"  # Super administrator
```

### Database Schema Enhancement

```sql
-- Add role column to users table
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user';

-- Add index for faster role queries
CREATE INDEX idx_users_role ON users(role);
```

### SQLAlchemy Model

```python
# backend/models/user.py
from sqlalchemy import Column, String, Enum
import enum

class UserRoleEnum(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER)  # ✅ NEW
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
```

---

## 🎨 Admin Dashboard UI Design

### 1. Admin Dashboard Page

```python
# frontend/pages/admin/dashboard.py
import streamlit as st
from utils.admin_auth import require_admin
from utils.auth import get_current_user

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# Require admin authentication
if not require_admin():
    st.error("⛔ Access Denied: Admin privileges required")
    st.stop()

st.title("🛡️ Admin Dashboard")

# Statistics Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Users", "1,234", "+23 today")

with col2:
    st.metric("Active Users", "1,180", "+12 today")

with col3:
    st.metric("New This Week", "156", "+5.2%")

with col4:
    st.metric("Login Rate", "85%", "+2.1%")

# Quick Actions
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👥 User Management", use_container_width=True):
        st.switch_page("pages/admin/users.py")

with col2:
    if st.button("📊 Analytics", use_container_width=True):
        st.switch_page("pages/admin/analytics.py")

with col3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.info("Settings page (coming soon)")

# Recent Activity
st.markdown("---")
st.subheader("📋 Recent Activity")

# Placeholder for recent activity log
st.dataframe({
    'Time': ['2 mins ago', '5 mins ago', '10 mins ago'],
    'Action': ['User Login', 'New Registration', 'Password Reset'],
    'User': ['user123', 'newuser', 'john_doe'],
    'Status': ['✅ Success', '✅ Success', '✅ Success']
}, use_container_width=True, hide_index=True)
```

### 2. User Management Page

```python
# frontend/pages/admin/users.py
import streamlit as st
import requests
from utils.admin_auth import require_admin
from utils.auth import get_auth_header

st.set_page_config(page_title="User Management", layout="wide")

# Require admin authentication
if not require_admin():
    st.error("⛔ Access Denied: Admin privileges required")
    st.stop()

st.title("👥 User Management")

# Search and Filter
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    search_query = st.text_input("🔍 Search users", placeholder="Search by ID, email, or name")

with col2:
    filter_role = st.selectbox("Role", ["All", "User", "Admin", "Super Admin"])

with col3:
    filter_status = st.selectbox("Status", ["All", "Active", "Inactive"])

# Fetch users from backend
if st.button("🔄 Refresh", type="primary"):
    st.rerun()

# User List
st.markdown("---")

# Fetch users from backend API
headers = get_auth_header()
response = requests.get(
    "http://backend:8000/api/admin/users",
    headers=headers,
    params={
        "search": search_query,
        "role": filter_role.lower() if filter_role != "All" else None,
        "status": filter_status.lower() if filter_status != "All" else None
    }
)

if response.status_code == 200:
    users = response.json()

    # Display users in a table
    for user in users:
        with st.expander(f"👤 {user['name']} ({user['user_id']})"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Email:** {user['email']}")
                st.markdown(f"**Role:** {user['role']}")
                st.markdown(f"**Status:** {'✅ Active' if user['is_active'] else '❌ Inactive'}")
                st.markdown(f"**Registered:** {user['created_at']}")
                st.markdown(f"**Last Login:** {user['last_login'] or 'Never'}")

            with col2:
                st.markdown("**Actions:**")

                if st.button(f"📝 Edit", key=f"edit_{user['id']}", use_container_width=True):
                    st.session_state.edit_user_id = user['id']
                    # Open edit modal

                if user['is_active']:
                    if st.button(f"🚫 Deactivate", key=f"deact_{user['id']}", use_container_width=True):
                        # Deactivate user
                        pass
                else:
                    if st.button(f"✅ Activate", key=f"act_{user['id']}", use_container_width=True):
                        # Activate user
                        pass

                if st.button(f"🔑 Reset Password", key=f"reset_{user['id']}", use_container_width=True):
                    # Send password reset
                    pass

                if st.button(f"🗑️ Delete", key=f"del_{user['id']}", use_container_width=True, type="secondary"):
                    # Delete user (with confirmation)
                    pass
else:
    st.error("Failed to fetch users from backend")
```

### 3. Analytics Page

```python
# frontend/pages/admin/analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.admin_auth import require_admin

st.set_page_config(page_title="Analytics", layout="wide")

# Require admin authentication
if not require_admin():
    st.error("⛔ Access Denied: Admin privileges required")
    st.stop()

st.title("📊 Analytics")

# Date range selector
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date")
with col2:
    end_date = st.date_input("End Date")

# User Registration Trend
st.subheader("📈 User Registration Trend")
# Placeholder data
dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
registrations = pd.DataFrame({
    'Date': dates,
    'Registrations': range(1, len(dates) + 1)
})
fig = px.line(registrations, x='Date', y='Registrations')
st.plotly_chart(fig, use_container_width=True)

# Login Activity
st.subheader("🔐 Login Activity")
# Placeholder data
st.line_chart({'Daily Logins': [100, 120, 115, 130, 125, 140, 135]})

# User Distribution by Role
st.subheader("👥 User Distribution")
col1, col2 = st.columns(2)

with col1:
    # Pie chart
    role_data = pd.DataFrame({
        'Role': ['User', 'Admin', 'Super Admin'],
        'Count': [1180, 50, 4]
    })
    fig = px.pie(role_data, values='Count', names='Role')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Bar chart
    st.bar_chart({'Active': [1180], 'Inactive': [54]})
```

---

## 🔧 Backend API Endpoints

### Admin User Management Endpoints

```python
# backend/api/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..dependencies import get_db, get_current_admin_user
from ..schemas.admin import UserResponse, UserUpdate
from ..models.user import User, UserRoleEnum

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only)

    Supports:
    - Pagination (skip, limit)
    - Search by user_id, email, or name
    - Filter by role
    - Filter by status (active/inactive)
    """
    query = db.query(User)

    # Search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.user_id.ilike(search_filter)) |
            (User.email.ilike(search_filter)) |
            (User.name.ilike(search_filter))
        )

    # Role filter
    if role and role != "all":
        query = query.filter(User.role == role)

    # Status filter
    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "inactive":
        query = query.filter(User.is_active == False)

    # Pagination
    users = query.offset(skip).limit(limit).all()

    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user account"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()

    return {"message": "User deactivated successfully"}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activate a user account"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()

    return {"message": "User activated successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deletion
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@router.get("/analytics/users")
async def get_user_analytics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user analytics (admin only)"""
    from sqlalchemy import func
    from datetime import datetime, timedelta

    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()

    # New users this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_this_week = db.query(func.count(User.id)).filter(
        User.created_at >= week_ago
    ).scalar()

    # New users today
    today = datetime.utcnow().date()
    new_today = db.query(func.count(User.id)).filter(
        func.date(User.created_at) == today
    ).scalar()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "new_this_week": new_this_week,
        "new_today": new_today
    }
```

---

## 🔒 Admin Authentication Utility

```python
# frontend/utils/admin_auth.py
"""
Admin Authentication Utilities
"""
import streamlit as st
from .auth import is_logged_in, get_current_user


def is_admin() -> bool:
    """
    Check if current user is an admin

    Returns:
        bool: True if user is admin or super_admin
    """
    if not is_logged_in():
        return False

    user = get_current_user()
    if not user:
        return False

    # Check user role (this should come from backend)
    user_role = user.get('role', 'user')
    return user_role in ['admin', 'super_admin']


def require_admin(redirect_to_home: bool = True) -> bool:
    """
    Require admin authentication for a page

    Args:
        redirect_to_home: Redirect to home if not admin

    Returns:
        bool: True if user is admin
    """
    if not is_logged_in():
        st.warning("⚠️ Please login first")
        if redirect_to_home:
            st.switch_page("pages/login.py")
        return False

    if not is_admin():
        st.error("⛔ Access Denied: Admin privileges required")
        if redirect_to_home:
            st.info("Redirecting to home page...")
            st.switch_page("finance.py")
        return False

    return True


def get_admin_menu_items():
    """Get admin-only menu items for navigation"""
    return [
        {"label": "🛡️ Admin Dashboard", "page": "pages/admin/dashboard.py"},
        {"label": "👥 User Management", "page": "pages/admin/users.py"},
        {"label": "📊 Analytics", "page": "pages/admin/analytics.py"},
    ]
```

---

## 🎨 Admin Navigation in Header

```python
# Update frontend/components/header.py

def render_header():
    # ... existing code ...

    with col2:
        cols = st.columns(4)
        with cols[0]:
            if st.button("시장현황", key="market", use_container_width=True):
                st.switch_page("finance.py")
        with cols[1]:
            if st.button("상장종목조회", key="stocks", use_container_width=True):
                st.switch_page("pages/listed_stock_retrieval.py")
        with cols[2]:
            if st.button("오늘의 공시", key="disclosure", use_container_width=True):
                st.switch_page("pages/disclosure_today.py")
        with cols[3]:
            if st.button("오늘의 뉴스", key="news", use_container_width=True):
                st.switch_page("pages/news_today.py")

        # ✅ NEW: Admin button (only for admins)
        if is_admin():
            with cols[4]:
                if st.button("🛡️ Admin", key="admin", use_container_width=True, type="secondary"):
                    st.switch_page("pages/admin/dashboard.py")
```

---

## 📊 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Add `role` column to users table
- [ ] Update User model with role field
- [ ] Create admin authentication utilities
- [ ] Update login to return user role

### Phase 2: Admin Pages (Week 2)
- [ ] Create admin dashboard page
- [ ] Create user management page
- [ ] Create analytics page
- [ ] Add admin navigation to header

### Phase 3: Backend APIs (Week 3)
- [ ] Implement admin user list API
- [ ] Implement user detail API
- [ ] Implement user update API
- [ ] Implement activate/deactivate API
- [ ] Implement delete user API
- [ ] Implement analytics API

### Phase 4: Integration (Week 4)
- [ ] Connect frontend to backend APIs
- [ ] Add pagination and search
- [ ] Add filters and sorting
- [ ] Implement user edit modal
- [ ] Add confirmation dialogs

### Phase 5: Polish (Week 5)
- [ ] Add loading states
- [ ] Add error handling
- [ ] Add success/failure notifications
- [ ] Add audit logging
- [ ] Security review

---

## 🔐 Security Considerations

1. **Role Verification**
   - Always verify admin role on backend
   - Never trust frontend role checks alone
   - Use JWT tokens with role claims

2. **Audit Logging**
   - Log all admin actions
   - Track who, what, when
   - Store in separate audit table

3. **Sensitive Data**
   - Never expose passwords
   - Hash sensitive data
   - Limit data exposure

4. **Rate Limiting**
   - Limit admin API calls
   - Prevent abuse
   - Add CAPTCHA for sensitive operations

---

## 📝 Quick Start Guide

### For Admins

1. **Login as Admin**
   ```
   - Use admin credentials
   - Navigate to "🛡️ Admin" in header
   ```

2. **View Users**
   ```
   - Click "👥 User Management"
   - Search, filter, sort users
   - View user details
   ```

3. **Manage Users**
   ```
   - Activate/deactivate accounts
   - Reset passwords
   - Edit user information
   - Delete users (with confirmation)
   ```

4. **View Analytics**
   ```
   - Click "📊 Analytics"
   - View registration trends
   - Check login activity
   - Monitor user distribution
   ```

---

## 💡 Future Enhancements

1. **Advanced Filters**
   - Filter by date range
   - Multiple role selection
   - Custom query builder

2. **Bulk Operations**
   - Bulk activate/deactivate
   - Bulk delete
   - Bulk email

3. **Export Data**
   - Export user list to CSV/Excel
   - Generate reports
   - Schedule automated reports

4. **Real-time Updates**
   - WebSocket for live updates
   - Real-time user count
   - Live activity feed

5. **Advanced Analytics**
   - User engagement metrics
   - Retention analysis
   - Cohort analysis
   - Custom dashboards

---

**Document Status:** Design Complete
**Next Step:** Begin Phase 1 Implementation
**Author:** Claude Code
**Date:** 2025-10-16
