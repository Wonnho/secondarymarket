# pages/admin_test_setup.py
"""
Admin Testing Setup Page
This page allows you to set admin role for testing purposes.
⚠️ FOR DEVELOPMENT/TESTING ONLY - Remove in production!
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.auth import is_logged_in, get_current_user
from utils.admin_auth import set_user_role_for_testing, is_admin

# 페이지 설정
st.set_page_config(page_title="Admin Testing Setup", page_icon="🧪", layout="wide")

st.title("🧪 Admin Testing Setup")
st.caption("⚠️ Development/Testing Only - Remove in Production!")

st.markdown("---")

# Check if logged in
if not is_logged_in():
    st.warning("⚠️ You need to be logged in to use this page.")
    st.info("Please login first, then come back to this page.")

    if st.button("Go to Login Page", type="primary"):
        st.switch_page("pages/login.py")
    st.stop()

# Get current user
user = get_current_user()

# Display current status
st.subheader("📊 Current Status")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**User Information:**")
    st.markdown(f"- **User ID:** `{user['user_id']}`")
    st.markdown(f"- **Name:** {user['user_name']}")
    st.markdown(f"- **Current Role:** `{user.get('role', 'user')}`")

with col2:
    st.markdown("**Permissions:**")
    current_role = user.get('role', 'user')

    if current_role == 'super_admin':
        st.success("✅ Super Admin - Full Access")
    elif current_role == 'admin':
        st.info("✅ Admin - Can manage users")
    else:
        st.warning("⚠️ Regular User - No admin access")

st.markdown("---")

# Role selection
st.subheader("🔧 Set Testing Role")

st.markdown("""
Select a role to test different permission levels:
- **User**: Regular user with no admin access
- **Admin**: Can view dashboard and manage regular users
- **Super Admin**: Can manage all users including admins
""")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👤 Set as User", use_container_width=True, type="secondary"):
        set_user_role_for_testing('user')
        st.rerun()

with col2:
    if st.button("🛡️ Set as Admin", use_container_width=True, type="primary"):
        set_user_role_for_testing('admin')
        st.rerun()

with col3:
    if st.button("⭐ Set as Super Admin", use_container_width=True, type="primary"):
        set_user_role_for_testing('super_admin')
        st.rerun()

st.markdown("---")

# Quick navigation
st.subheader("🚀 Quick Navigation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Finance Page", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if is_admin():
        if st.button("🛡️ Admin Dashboard", use_container_width=True, type="primary"):
            st.switch_page("pages/admin/dashboard.py")
    else:
        st.button("🛡️ Admin Dashboard", use_container_width=True, disabled=True)
        st.caption("Requires admin role")

with col3:
    if is_admin():
        if st.button("👥 User Management", use_container_width=True, type="primary"):
            st.switch_page("pages/admin/users.py")
    else:
        st.button("👥 User Management", use_container_width=True, disabled=True)
        st.caption("Requires admin role")

with col4:
    if is_admin():
        if st.button("📊 Analytics", use_container_width=True, type="primary"):
            st.switch_page("pages/admin/analytics.py")
    else:
        st.button("📊 Analytics", use_container_width=True, disabled=True)
        st.caption("Requires admin role")

st.markdown("---")

# Testing checklist
st.subheader("✅ Testing Checklist")

st.markdown("""
### Test as Regular User:
1. Set role to "User"
2. Try accessing admin dashboard (should be denied)
3. Verify no admin options in header

### Test as Admin:
1. Set role to "Admin"
2. Access admin dashboard (should work)
3. Go to user management
4. Try to manage regular users (should work)
5. Try to manage admin users (should be restricted)

### Test as Super Admin:
1. Set role to "Super Admin"
2. Access admin dashboard (should work)
3. Go to user management
4. Verify you can manage all users including admins

### Test User Management Features:
1. Search for users by name/email/ID
2. Filter by role
3. Filter by status
4. View user details
5. Test activate/deactivate
6. Test password reset
7. Test delete with confirmation
""")

st.markdown("---")

# Warning
st.error("""
⚠️ **IMPORTANT: Security Warning**

This page is for **DEVELOPMENT AND TESTING ONLY**!

**Before deploying to production:**
1. Delete this file (`pages/admin_test_setup.py`)
2. Remove `set_user_role_for_testing()` function from `utils/admin_auth.py`
3. Ensure roles are managed through backend API only
4. Never allow frontend role assignment in production

**Why this is dangerous:**
- Anyone can change their role to admin
- No authentication or authorization
- Completely bypasses security

**Production approach:**
- Roles stored in database
- Assigned by super admin only
- Validated on backend for every request
""")

st.markdown("---")

# Footer
st.caption("Admin Testing Setup v1.0 | Development Tool")
