"""
Session Manager for Persistent Login
Simplified version using Streamlit's built-in session state
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional


def init_session_state():
    """
    Initialize session state with all required fields
    """
    # Login state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # User info
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'role' not in st.session_state:
        st.session_state.role = 'user'

    # Session timing
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = None


def save_session(user_id: str, user_name: str, access_token: str, role: str = 'user'):
    """
    Save user session data

    Args:
        user_id: User ID
        user_name: User name
        access_token: JWT access token
        role: User role (default: 'user')
    """
    current_time = datetime.now()

    st.session_state.logged_in = True
    st.session_state.user_id = user_id
    st.session_state.user_name = user_name
    st.session_state.access_token = access_token
    st.session_state.role = role
    st.session_state.login_time = current_time
    st.session_state.last_activity = current_time


def update_last_activity():
    """
    Update last activity timestamp
    """
    if st.session_state.get('logged_in', False):
        st.session_state.last_activity = datetime.now()


def check_session_timeout() -> bool:
    """
    Check if session has timed out (1 hour inactivity)

    Returns:
        bool: True if session is still valid, False if timed out
    """
    if not st.session_state.get('logged_in', False):
        return False

    last_activity = st.session_state.get('last_activity')
    if not last_activity:
        # No last activity recorded, consider valid
        st.session_state.last_activity = datetime.now()
        return True

    # Calculate time since last activity
    now = datetime.now()
    inactive_duration = now - last_activity

    # Check if inactive for more than 1 hour
    if inactive_duration > timedelta(hours=1):
        clear_session()
        return False

    # Update last activity
    update_last_activity()
    return True


def clear_session():
    """
    Clear all session data (logout)
    """
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.access_token = None
    st.session_state.role = 'user'
    st.session_state.login_time = None
    st.session_state.last_activity = None


def is_logged_in() -> bool:
    """
    Check if user is logged in

    Returns:
        bool: True if logged in, False otherwise
    """
    return st.session_state.get('logged_in', False)


def get_current_user() -> Optional[dict]:
    """
    Get current logged in user info

    Returns:
        Optional[dict]: User info or None
    """
    if not is_logged_in():
        return None

    return {
        'user_id': st.session_state.user_id,
        'user_name': st.session_state.user_name,
        'access_token': st.session_state.access_token,
        'role': st.session_state.get('role', 'user')
    }


def get_session_info() -> dict:
    """
    Get detailed session information

    Returns:
        dict: Session info including durations
    """
    if not is_logged_in():
        return {
            'logged_in': False,
            'message': 'Not logged in'
        }

    now = datetime.now()
    login_time = st.session_state.get('login_time')
    last_activity = st.session_state.get('last_activity')

    info = {
        'logged_in': True,
        'user_id': st.session_state.user_id,
        'user_name': st.session_state.user_name,
        'role': st.session_state.get('role', 'user'),
    }

    if login_time:
        session_duration = now - login_time
        info['login_time'] = login_time.strftime('%Y-%m-%d %H:%M:%S')
        info['session_duration'] = str(session_duration).split('.')[0]

    if last_activity:
        inactive_duration = now - last_activity
        time_until_logout = timedelta(hours=1) - inactive_duration

        info['last_activity'] = last_activity.strftime('%Y-%m-%d %H:%M:%S')
        info['inactive_duration'] = str(inactive_duration).split('.')[0]

        if time_until_logout.total_seconds() > 0:
            info['time_until_logout'] = str(time_until_logout).split('.')[0]
        else:
            info['time_until_logout'] = '만료됨'

    return info


def set_user_role(role: str):
    """
    Set user role (for testing purposes)

    Args:
        role: User role ('user', 'admin', 'super_admin')
    """
    if st.session_state.get('logged_in', False):
        st.session_state.role = role
        st.success(f"✅ 역할이 '{role}'로 변경되었습니다.")
