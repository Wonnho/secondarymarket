"""
Session Manager for Persistent Login
Uses cookies to persist login state across page refreshes
"""
import streamlit as st
from datetime import datetime, timedelta
import json
import hashlib
import base64


def encode_session_data(data: dict) -> str:
    """
    Encode session data to base64 string

    Args:
        data: Session data dictionary

    Returns:
        str: Base64 encoded session data
    """
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()


def decode_session_data(encoded: str) -> dict:
    """
    Decode base64 string to session data

    Args:
        encoded: Base64 encoded session data

    Returns:
        dict: Session data dictionary
    """
    try:
        json_str = base64.b64decode(encoded.encode()).decode()
        return json.loads(json_str)
    except Exception:
        return {}


def save_session_to_cookie(user_id: str, user_name: str, access_token: str, role: str = 'user'):
    """
    Save session data to browser cookie

    Args:
        user_id: User ID
        user_name: User name
        access_token: JWT access token
        role: User role (default: 'user')
    """
    # Create session data
    session_data = {
        'user_id': user_id,
        'user_name': user_name,
        'access_token': access_token,
        'role': role,
        'login_time': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat()
    }

    # Encode session data
    encoded_session = encode_session_data(session_data)

    # Save to cookie using Streamlit's experimental feature
    # Cookie expires in 7 days (but we'll check activity timeout separately)
    cookie_expiry = datetime.now() + timedelta(days=7)

    # Store in session state for immediate use
    st.session_state.session_cookie = encoded_session
    st.session_state.logged_in = True
    st.session_state.user_id = user_id
    st.session_state.user_name = user_name
    st.session_state.access_token = access_token
    st.session_state.role = role
    st.session_state.login_time = session_data['login_time']
    st.session_state.last_activity = session_data['last_activity']

    # Use JavaScript to set cookie (workaround for Streamlit)
    set_cookie_js = f"""
    <script>
        const setCookie = (name, value, days) => {{
            const expires = new Date();
            expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
            document.cookie = name + '=' + value + ';expires=' + expires.toUTCString() + ';path=/;SameSite=Strict';
        }};
        setCookie('session_data', '{encoded_session}', 7);
    </script>
    """
    st.components.v1.html(set_cookie_js, height=0, width=0)


def load_session_from_cookie() -> bool:
    """
    Load session data from browser cookie

    Returns:
        bool: True if session loaded successfully, False otherwise
    """
    # Try to get cookie value using JavaScript
    get_cookie_js = """
    <script>
        const getCookie = (name) => {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) {
                return parts.pop().split(';').shift();
            }
            return null;
        };

        const sessionData = getCookie('session_data');
        if (sessionData) {
            // Send to Streamlit via query params (workaround)
            window.parent.postMessage({type: 'session_data', value: sessionData}, '*');
        }
    </script>
    """

    # For now, check if session exists in session_state (server-side session)
    # This is a fallback since Streamlit doesn't easily access cookies
    if 'session_cookie' in st.session_state and st.session_state.session_cookie:
        try:
            session_data = decode_session_data(st.session_state.session_cookie)

            # Check if session is still valid (not expired)
            if is_session_valid(session_data):
                # Restore session state
                st.session_state.logged_in = True
                st.session_state.user_id = session_data.get('user_id')
                st.session_state.user_name = session_data.get('user_name')
                st.session_state.access_token = session_data.get('access_token')
                st.session_state.role = session_data.get('role', 'user')
                st.session_state.login_time = session_data.get('login_time')
                st.session_state.last_activity = session_data.get('last_activity')

                # Update last activity time
                update_last_activity()

                return True
        except Exception as e:
            print(f"Error loading session: {e}")

    return False


def is_session_valid(session_data: dict) -> bool:
    """
    Check if session is still valid (not expired due to inactivity)

    Args:
        session_data: Session data dictionary

    Returns:
        bool: True if valid, False if expired
    """
    try:
        last_activity_str = session_data.get('last_activity')
        if not last_activity_str:
            return False

        last_activity = datetime.fromisoformat(last_activity_str)
        now = datetime.now()

        # Check if inactive for more than 1 hour
        inactive_duration = now - last_activity
        if inactive_duration > timedelta(hours=1):
            return False

        return True
    except Exception:
        return False


def update_last_activity():
    """
    Update last activity timestamp in session
    """
    current_time = datetime.now().isoformat()
    st.session_state.last_activity = current_time

    # Update cookie as well
    if 'session_cookie' in st.session_state:
        try:
            session_data = decode_session_data(st.session_state.session_cookie)
            session_data['last_activity'] = current_time
            st.session_state.session_cookie = encode_session_data(session_data)
        except Exception:
            pass


def check_and_enforce_timeout() -> bool:
    """
    Check if session has timed out due to inactivity
    If timed out, logout user

    Returns:
        bool: True if session is still valid, False if timed out
    """
    if not st.session_state.get('logged_in', False):
        return False

    last_activity_str = st.session_state.get('last_activity')
    if not last_activity_str:
        return True  # No timestamp, allow for now

    try:
        last_activity = datetime.fromisoformat(last_activity_str)
        now = datetime.now()

        inactive_duration = now - last_activity

        # Auto-logout after 1 hour of inactivity
        if inactive_duration > timedelta(hours=1):
            clear_session()
            st.warning("⏰ 1시간 동안 활동이 없어 자동으로 로그아웃되었습니다.")
            st.info("다시 로그인해주세요.")
            return False

        # Update activity timestamp
        update_last_activity()
        return True

    except Exception:
        return True


def clear_session():
    """
    Clear session data (logout)
    """
    # Clear session state
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.access_token = None
    st.session_state.role = 'user'
    st.session_state.session_cookie = None
    st.session_state.login_time = None
    st.session_state.last_activity = None

    # Clear cookie
    clear_cookie_js = """
    <script>
        document.cookie = 'session_data=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    </script>
    """
    st.components.v1.html(clear_cookie_js, height=0, width=0)


def get_session_info() -> dict:
    """
    Get current session information

    Returns:
        dict: Session info including login time and last activity
    """
    if not st.session_state.get('logged_in', False):
        return {}

    login_time_str = st.session_state.get('login_time')
    last_activity_str = st.session_state.get('last_activity')

    info = {
        'user_id': st.session_state.get('user_id'),
        'user_name': st.session_state.get('user_name'),
        'role': st.session_state.get('role', 'user'),
    }

    if login_time_str:
        info['login_time'] = datetime.fromisoformat(login_time_str)
        info['session_duration'] = datetime.now() - info['login_time']

    if last_activity_str:
        info['last_activity'] = datetime.fromisoformat(last_activity_str)
        info['inactive_duration'] = datetime.now() - info['last_activity']
        info['time_until_logout'] = timedelta(hours=1) - info['inactive_duration']

    return info
