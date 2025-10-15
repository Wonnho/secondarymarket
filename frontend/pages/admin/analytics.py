# pages/admin/analytics.py
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from components.header import render_header
from utils.admin_auth import require_admin
from utils.auth import get_current_user

# 페이지 설정
st.set_page_config(page_title="Analytics", layout="wide", page_icon="📊")

# 관리자 권한 확인
if not require_admin(redirect_to_home=True):
    st.stop()

# 헤더 렌더링
render_header()

# Analytics Dashboard
st.title("📊 Analytics Dashboard")

user = get_current_user()
st.markdown(f"Analytics for **{user['user_name']}** ({user.get('role', 'admin')})")

st.markdown("---")

# Time Period Filter
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 12 Months", "All Time"],
        index=1
    )

with col2:
    comparison = st.selectbox(
        "Compare with",
        ["Previous Period", "Same Period Last Year", "No Comparison"],
        index=0
    )

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Key Metrics Row
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Revenue",
        value="$124,567",
        delta="+15.3%",
        help="Total revenue in selected period"
    )

with col2:
    st.metric(
        label="New Users",
        value="1,234",
        delta="+23.1%",
        help="New user registrations"
    )

with col3:
    st.metric(
        label="Active Users",
        value="8,945",
        delta="+5.7%",
        help="Users who logged in during this period"
    )

with col4:
    st.metric(
        label="Conversion Rate",
        value="12.5%",
        delta="+2.3%",
        help="Signup to active user conversion"
    )

st.markdown("---")

# User Registration Trend
st.subheader("👥 User Registration Trend")

# Generate sample data for the chart
days = 30
dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(days, 0, -1)]
registrations = [15 + (i % 7) * 5 + (i % 3) * 3 for i in range(days)]

registration_df = pd.DataFrame({
    'Date': dates,
    'New Users': registrations
})

st.line_chart(registration_df.set_index('Date'))

# Two column layout for additional charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("---")
    st.subheader("📱 Login Activity")

    # Sample login activity data
    hours = [f"{i:02d}:00" for i in range(24)]
    logins = [50 + (i % 8) * 20 + (i % 3) * 10 for i in range(24)]

    login_df = pd.DataFrame({
        'Hour': hours,
        'Logins': logins
    })

    st.bar_chart(login_df.set_index('Hour'))
    st.caption("Login activity by hour of day")

with col2:
    st.markdown("---")
    st.subheader("🎯 User Engagement")

    # Sample engagement data
    engagement_data = pd.DataFrame({
        'Category': ['Daily Active', 'Weekly Active', 'Monthly Active', 'Inactive'],
        'Users': [3500, 2800, 1800, 800]
    })

    st.bar_chart(engagement_data.set_index('Category'))
    st.caption("User engagement levels")

st.markdown("---")

# Geographic Distribution
st.subheader("🌍 Geographic Distribution")

col1, col2 = st.columns(2)

with col1:
    # Top countries
    country_data = pd.DataFrame({
        'Country': ['South Korea', 'United States', 'Japan', 'China', 'United Kingdom'],
        'Users': [4500, 2100, 1200, 890, 650]
    })

    st.markdown("**Top Countries**")
    st.dataframe(
        country_data,
        column_config={
            'Country': st.column_config.TextColumn('Country', width='medium'),
            'Users': st.column_config.NumberColumn('Users', width='small', format='%d'),
        },
        use_container_width=True,
        hide_index=True
    )

with col2:
    # User growth by region
    region_growth = pd.DataFrame({
        'Region': ['Asia', 'North America', 'Europe', 'South America', 'Africa'],
        'Growth %': [23.5, 18.2, 12.8, 8.4, 5.1]
    })

    st.markdown("**Growth by Region**")
    st.bar_chart(region_growth.set_index('Region'))

st.markdown("---")

# Feature Usage Statistics
st.subheader("⚡ Feature Usage")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Most Used Features**")
    feature_usage = pd.DataFrame({
        'Feature': ['Dashboard', 'Market Data', 'Portfolio', 'News', 'Settings'],
        'Usage Count': [15420, 12890, 9876, 7654, 3210],
        'Avg Time (min)': [8.5, 12.3, 6.7, 4.2, 2.1]
    })

    st.dataframe(
        feature_usage,
        column_config={
            'Feature': st.column_config.TextColumn('Feature', width='medium'),
            'Usage Count': st.column_config.NumberColumn('Usage Count', width='small', format='%d'),
            'Avg Time (min)': st.column_config.NumberColumn('Avg Time (min)', width='small', format='%.1f'),
        },
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.markdown("**User Satisfaction**")
    satisfaction_data = pd.DataFrame({
        'Rating': ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star'],
        'Count': [2340, 1890, 456, 123, 45]
    })

    st.bar_chart(satisfaction_data.set_index('Rating'))
    st.caption("User ratings and feedback")

st.markdown("---")

# Retention Cohort Analysis
st.subheader("📅 User Retention")

# Sample cohort data
cohort_data = pd.DataFrame({
    'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    'Retention Rate': [100, 78, 65, 58]
})

st.line_chart(cohort_data.set_index('Week'))
st.caption("User retention rate over time")

# Detailed retention table
st.markdown("**Detailed Retention Metrics**")
retention_metrics = pd.DataFrame({
    'Period': ['Day 1', 'Day 7', 'Day 14', 'Day 30', 'Day 90'],
    'Retention Rate': ['100%', '78%', '65%', '58%', '45%'],
    'Active Users': [1234, 962, 802, 716, 555],
    'Churned Users': [0, 272, 160, 86, 161]
})

st.dataframe(retention_metrics, use_container_width=True, hide_index=True)

st.markdown("---")

# Revenue Analytics
st.subheader("💰 Revenue Analytics")

col1, col2 = st.columns(2)

with col1:
    # Revenue by source
    revenue_data = pd.DataFrame({
        'Source': ['Subscriptions', 'Trading Fees', 'Premium Features', 'Advertisements'],
        'Revenue': [45000, 38000, 28000, 13567]
    })

    st.markdown("**Revenue by Source**")
    st.bar_chart(revenue_data.set_index('Source'))

with col2:
    # Revenue trend
    revenue_trend = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [95000, 102000, 108000, 115000, 118000, 124567]
    })

    st.markdown("**Revenue Trend**")
    st.line_chart(revenue_trend.set_index('Month'))

st.markdown("---")

# Export Options
st.subheader("📥 Export Data")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Export to CSV", use_container_width=True):
        st.info("CSV export feature coming soon...")

with col2:
    if st.button("📈 Export to Excel", use_container_width=True):
        st.info("Excel export feature coming soon...")

with col3:
    if st.button("📄 Generate Report", use_container_width=True):
        st.info("Report generation feature coming soon...")

with col4:
    if st.button("📧 Email Report", use_container_width=True):
        st.info("Email report feature coming soon...")

# Navigation
st.markdown("---")
if st.button("← Back to Dashboard", use_container_width=True):
    st.switch_page("pages/admin/dashboard.py")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("⚠️ Current implementation uses mock data. Backend integration required for production.")
