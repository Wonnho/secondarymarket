"""
Admin Authentication Utilities
관리자 인증 관련 유틸리티 함수들
"""
import streamlit as st
from typing import List, Dict
from .auth import is_logged_in, get_current_user
from . import session_manager


def is_admin() -> bool:
    """
    현재 사용자가 관리자인지 확인

    Returns:
        bool: 관리자 권한 여부
    """
    if not is_logged_in():
        return False

    user = get_current_user()
    if not user:
        return False

    # 사용자 역할 확인 (백엔드에서 받아온 정보)
    user_role = user.get('role', 'user')
    return user_role in ['admin', 'super_admin']


def is_super_admin() -> bool:
    """
    현재 사용자가 슈퍼 관리자인지 확인

    Returns:
        bool: 슈퍼 관리자 권한 여부
    """
    if not is_logged_in():
        return False

    user = get_current_user()
    if not user:
        return False

    user_role = user.get('role', 'user')
    return user_role == 'super_admin'


def require_admin(redirect_to_home: bool = True) -> bool:
    """
    관리자 인증이 필요한 페이지에서 사용

    Args:
        redirect_to_home: 권한이 없을 경우 홈으로 리다이렉트 여부

    Returns:
        bool: 관리자 권한 여부
    """
    if not is_logged_in():
        st.warning("⚠️ 로그인이 필요한 페이지입니다.")
        if redirect_to_home:
            st.info("로그인 페이지로 이동합니다...")
            st.switch_page("pages/login.py")
        return False

    if not is_admin():
        st.error("⛔ 접근 거부: 관리자 권한이 필요합니다.")
        if redirect_to_home:
            st.info("메인 페이지로 이동합니다...")
            st.switch_page("app.py")
        return False

    return True


def require_super_admin(redirect_to_home: bool = True) -> bool:
    """
    슈퍼 관리자 인증이 필요한 페이지에서 사용

    Args:
        redirect_to_home: 권한이 없을 경우 홈으로 리다이렉트 여부

    Returns:
        bool: 슈퍼 관리자 권한 여부
    """
    if not is_logged_in():
        st.warning("⚠️ 로그인이 필요한 페이지입니다.")
        if redirect_to_home:
            st.info("로그인 페이지로 이동합니다...")
            st.switch_page("pages/login.py")
        return False

    if not is_super_admin():
        st.error("⛔ 접근 거부: 슈퍼 관리자 권한이 필요합니다.")
        if redirect_to_home:
            st.info("메인 페이지로 이동합니다...")
            st.switch_page("app.py")
        return False

    return True


def get_admin_menu_items() -> List[Dict[str, str]]:
    """
    관리자 메뉴 항목 반환

    Returns:
        List[Dict[str, str]]: 메뉴 항목 리스트
    """
    return [
        {"label": "🛡️ Admin Dashboard", "page": "pages/admin/dashboard.py", "icon": "🛡️"},
        {"label": "👥 User Management", "page": "pages/admin/users.py", "icon": "👥"},
        {"label": "📊 Analytics", "page": "pages/admin/analytics.py", "icon": "📊"},
    ]


def can_manage_user(target_user_role: str) -> bool:
    """
    특정 역할의 사용자를 관리할 수 있는지 확인

    Args:
        target_user_role: 대상 사용자의 역할

    Returns:
        bool: 관리 가능 여부

    Rules:
    - super_admin can manage everyone
    - admin can manage users only
    - user cannot manage anyone
    """
    if not is_logged_in():
        return False

    user = get_current_user()
    if not user:
        return False

    current_role = user.get('role', 'user')

    # 슈퍼 관리자는 모든 사용자 관리 가능
    if current_role == 'super_admin':
        return True

    # 일반 관리자는 일반 사용자만 관리 가능
    if current_role == 'admin':
        return target_user_role == 'user'

    # 일반 사용자는 관리 불가
    return False


def log_admin_action(action: str, target: str, details: str = ""):
    """
    관리자 액션을 로깅

    Args:
        action: 수행한 액션 (예: "delete_user", "deactivate_user")
        target: 대상 (예: 사용자 ID)
        details: 추가 상세 정보

    TODO: 실제 백엔드 API와 연동하여 감사 로그 저장
    """
    if not is_admin():
        return

    user = get_current_user()
    if not user:
        return

    # 임시: 세션 상태에 로그 저장 (실제로는 백엔드 API로 전송)
    if 'admin_logs' not in st.session_state:
        st.session_state.admin_logs = []

    from datetime import datetime
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'admin_id': user['user_id'],
        'admin_name': user['user_name'],
        'action': action,
        'target': target,
        'details': details
    }

    st.session_state.admin_logs.append(log_entry)

    # TODO: 백엔드 API 호출
    # requests.post("http://backend:8000/api/admin/audit-log", json=log_entry)


def get_recent_admin_logs(limit: int = 10) -> List[Dict]:
    """
    최근 관리자 로그 가져오기

    Args:
        limit: 가져올 로그 개수

    Returns:
        List[Dict]: 로그 엔트리 리스트
    """
    if not is_admin():
        return []

    if 'admin_logs' not in st.session_state:
        return []

    logs = st.session_state.admin_logs
    return logs[-limit:] if len(logs) > limit else logs


def set_user_role_for_testing(role: str):
    """
    테스트용: 현재 사용자의 역할 설정

    Args:
        role: 설정할 역할 ('user', 'admin', 'super_admin')

    주의: 개발/테스트 환경에서만 사용! 프로덕션에서는 제거 필요
    """
    session_manager.set_user_role(role)
