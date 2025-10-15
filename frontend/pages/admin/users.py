# pages/admin/users.py
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from components.header import render_header
from utils.admin_auth import require_admin, log_admin_action, can_manage_user
from utils.auth import get_current_user

# 페이지 설정
st.set_page_config(page_title="User Management", layout="wide", page_icon="👥")

# 관리자 권한 확인
if not require_admin(redirect_to_home=True):
    st.stop()

# 헤더 렌더링
render_header()

# User Management
st.title("👥 User Management")

# Search and Filter
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

with col1:
    search_query = st.text_input(
        "🔍 Search users",
        placeholder="Search by ID, email, or name",
        label_visibility="collapsed"
    )

with col2:
    filter_role = st.selectbox(
        "Role",
        ["All", "User", "Admin", "Super Admin"],
        label_visibility="collapsed"
    )

with col3:
    filter_status = st.selectbox(
        "Status",
        ["All", "Active", "Inactive"],
        label_visibility="collapsed"
    )

with col4:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# TODO: Fetch from backend API
# For now, show sample data
sample_users = [
    {
        'id': 1,
        'user_id': 'admin',
        'email': 'admin@example.com',
        'name': 'Administrator',
        'role': 'admin',
        'is_active': True,
        'created_at': '2024-01-01 10:00:00',
        'last_login': '2025-10-16 09:30:00'
    },
    {
        'id': 2,
        'user_id': 'user123',
        'email': 'user123@example.com',
        'name': 'John Doe',
        'role': 'user',
        'is_active': True,
        'created_at': '2024-06-15 14:20:00',
        'last_login': '2025-10-15 18:45:00'
    },
    {
        'id': 3,
        'user_id': 'inactive_user',
        'email': 'inactive@example.com',
        'name': 'Jane Smith',
        'role': 'user',
        'is_active': False,
        'created_at': '2024-03-20 09:15:00',
        'last_login': '2024-12-01 16:20:00'
    },
]

# Filter users
filtered_users = sample_users

if search_query:
    filtered_users = [
        u for u in filtered_users
        if search_query.lower() in u['user_id'].lower()
        or search_query.lower() in u['email'].lower()
        or search_query.lower() in u['name'].lower()
    ]

if filter_role != "All":
    role_map = {"User": "user", "Admin": "admin", "Super Admin": "super_admin"}
    filtered_users = [u for u in filtered_users if u['role'] == role_map[filter_role]]

if filter_status != "All":
    is_active = filter_status == "Active"
    filtered_users = [u for u in filtered_users if u['is_active'] == is_active]

# Display results count
st.info(f"📊 Found {len(filtered_users)} user(s)")

# Display users
if filtered_users:
    for user in filtered_users:
        with st.expander(
            f"{'✅' if user['is_active'] else '❌'} {user['name']} (@{user['user_id']}) - {user['role'].upper()}",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### User Information")
                st.markdown(f"**User ID:** `{user['user_id']}`")
                st.markdown(f"**Email:** {user['email']}")
                st.markdown(f"**Name:** {user['name']}")
                st.markdown(f"**Role:** `{user['role']}`")
                st.markdown(f"**Status:** {'✅ Active' if user['is_active'] else '❌ Inactive'}")
                st.markdown(f"**Registered:** {user['created_at']}")
                st.markdown(f"**Last Login:** {user['last_login'] or 'Never'}")

            with col2:
                st.markdown("### Actions")

                # Check if current admin can manage this user
                can_manage = can_manage_user(user['role'])

                if can_manage:
                    if st.button(
                        f"📝 Edit Profile",
                        key=f"edit_{user['id']}",
                        use_container_width=True
                    ):
                        st.info("📝 Edit profile feature coming soon...")
                        log_admin_action("view_edit_form", user['user_id'], "Opened edit form")

                    if user['is_active']:
                        if st.button(
                            f"🚫 Deactivate",
                            key=f"deact_{user['id']}",
                            use_container_width=True,
                            type="secondary"
                        ):
                            st.warning(f"⚠️ Deactivating user: {user['user_id']}")
                            log_admin_action("deactivate_user", user['user_id'], "User deactivated")
                            st.success("✅ User deactivated successfully")
                            st.balloons()
                    else:
                        if st.button(
                            f"✅ Activate",
                            key=f"act_{user['id']}",
                            use_container_width=True,
                            type="primary"
                        ):
                            st.success(f"✅ Activating user: {user['user_id']}")
                            log_admin_action("activate_user", user['user_id'], "User activated")
                            st.balloons()

                    if st.button(
                        f"🔑 Reset Password",
                        key=f"reset_{user['id']}",
                        use_container_width=True
                    ):
                        st.info(f"📧 Password reset email sent to {user['email']}")
                        log_admin_action("reset_password", user['user_id'], "Password reset initiated")

                    st.markdown("---")

                    if st.button(
                        f"🗑️ Delete User",
                        key=f"del_{user['id']}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.error(f"⚠️ This will permanently delete user: {user['user_id']}")
                        st.warning("This action cannot be undone!")

                        # Confirmation required
                        if st.checkbox(f"I confirm deletion of {user['user_id']}", key=f"confirm_del_{user['id']}"):
                            if st.button(f"⚠️ Confirm Delete", key=f"confirm_btn_{user['id']}", type="secondary"):
                                log_admin_action("delete_user", user['user_id'], "User deleted permanently")
                                st.error("🗑️ User deleted successfully")
                                st.rerun()
                else:
                    st.warning(f"⛔ Cannot manage {user['role']} users")
                    st.caption("Insufficient permissions")

else:
    st.warning("No users found matching the search criteria")

# Add New User Button
st.markdown("---")
if st.button("➕ Add New User", type="primary", use_container_width=True):
    st.info("➕ Add new user feature coming soon...")
    log_admin_action("view_add_user_form", "N/A", "Opened add user form")

# Back to Dashboard
if st.button("← Back to Dashboard", use_container_width=True):
    st.switch_page("pages/admin/dashboard.py")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("⚠️ Current implementation uses mock data. Backend integration required for production.")
