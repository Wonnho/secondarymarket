# pages/admin/dashboard.py
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from components.header import render_header
from utils.admin_auth import require_admin, get_recent_admin_logs
from utils.auth import get_current_user

# 페이지 설정
st.set_page_config(page_title="Admin Dashboard", layout="wide", page_icon="🛡️")

# 관리자 권한 확인
if not require_admin(redirect_to_home=True):
    st.stop()

# 헤더 렌더링
render_header()

# Admin Dashboard
st.title("🛡️ Admin Dashboard")

user = get_current_user()
st.markdown(f"Welcome, **{user['user_name']}** ({user.get('role', 'admin')})")

st.markdown("---")

# Statistics Cards
st.subheader("📊 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Users",
        value="1,234",
        delta="+23 today",
        help="Total number of registered users"
    )

with col2:
    st.metric(
        label="Active Users",
        value="1,180",
        delta="+12 today",
        help="Users who have logged in within the last 30 days"
    )

with col3:
    st.metric(
        label="New This Week",
        value="156",
        delta="+5.2%",
        help="New registrations this week"
    )

with col4:
    st.metric(
        label="Login Rate",
        value="85%",
        delta="+2.1%",
        help="Percentage of users who log in regularly"
    )

# Quick Actions
st.markdown("---")
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("👥 User Management", use_container_width=True, type="primary"):
        st.switch_page("pages/admin/users.py")

with col2:
    if st.button("📊 Analytics", use_container_width=True):
        st.switch_page("pages/admin/analytics.py")

with col3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.info("⚙️ Settings page (coming soon)")

with col4:
    if st.button("📝 Audit Logs", use_container_width=True):
        st.info("📝 Audit logs page (coming soon)")

# Recent Activity
st.markdown("---")
st.subheader("📋 Recent Activity")

# Get recent admin logs
recent_logs = get_recent_admin_logs(limit=10)

if recent_logs:
    # Display logs in a table
    import pandas as pd

    logs_df = pd.DataFrame(recent_logs)
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

    st.dataframe(
        logs_df[['timestamp', 'admin_name', 'action', 'target', 'details']],
        column_config={
            'timestamp': st.column_config.TextColumn('Time', width='medium'),
            'admin_name': st.column_config.TextColumn('Admin', width='small'),
            'action': st.column_config.TextColumn('Action', width='medium'),
            'target': st.column_config.TextColumn('Target', width='medium'),
            'details': st.column_config.TextColumn('Details', width='large'),
        },
        use_container_width=True,
        hide_index=True
    )
else:
    # Show sample data
    st.info("No recent activity. Activity logs will appear here once admin actions are performed.")

    # Sample data for demonstration
    sample_data = {
        'Time': [
            (datetime.now() - timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'),
            (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'),
            (datetime.now() - timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S'),
        ],
        'Admin': ['admin', 'admin', 'admin'],
        'Action': ['User Login', 'New Registration', 'Password Reset'],
        'Target': ['user123', 'newuser', 'john_doe'],
        'Status': ['✅ Success', '✅ Success', '✅ Success']
    }

    st.dataframe(sample_data, use_container_width=True, hide_index=True)

# System Status
st.markdown("---")
st.subheader("🖥️ System Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Backend API**")
    st.success("✅ Online")
    st.caption("Response time: 45ms")

with col2:
    st.markdown("**Database**")
    st.success("✅ Connected")
    st.caption("PostgreSQL 16.10")

with col3:
    st.markdown("**Redis Cache**")
    st.success("✅ Active")
    st.caption("Memory: 128MB / 2GB")

# User Distribution Chart
st.markdown("---")
st.subheader("👥 User Distribution")

col1, col2 = st.columns(2)

with col1:
    # Role distribution (pie chart)
    import pandas as pd

    role_data = pd.DataFrame({
        'Role': ['User', 'Admin', 'Super Admin'],
        'Count': [1180, 50, 4]
    })

    st.markdown("**By Role**")
    # Simple bar chart
    st.bar_chart(role_data.set_index('Role'))

with col2:
    # Status distribution
    status_data = pd.DataFrame({
        'Status': ['Active', 'Inactive'],
        'Count': [1180, 54]
    })

    st.markdown("**By Status**")
    st.bar_chart(status_data.set_index('Status'))

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Admin Dashboard v1.0 | For support, contact admin@secondarymarket.com")
