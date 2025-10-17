"""
Authentication Utility Module
인증 관련 유틸리티 함수들
"""
import streamlit as st
from typing import Optional, Tuple
from utils import session_manager


def init_session_state():
    """세션 상태 초기화 및 타임아웃 체크"""
    # Initialize all session state variables
    session_manager.init_session_state()

    # Check for timeout if logged in
    if session_manager.is_logged_in():
        if not session_manager.check_session_timeout():
            st.warning("⏰ 1시간 동안 활동이 없어 자동으로 로그아웃되었습니다.")
            st.info("다시 로그인해주세요.")


def is_logged_in() -> bool:
    """
    로그인 상태 확인

    Returns:
        bool: 로그인 여부
    """
    return session_manager.is_logged_in()


def get_current_user() -> Optional[dict]:
    """
    현재 로그인한 사용자 정보 가져오기

    Returns:
        Optional[dict]: 사용자 정보 딕셔너리 또는 None
    """
    return session_manager.get_current_user()


def login_user(user_id: str, user_name: str, access_token: Optional[str] = None, role: str = 'user'):
    """
    사용자 로그인 처리 및 세션 저장

    Args:
        user_id: 사용자 ID
        user_name: 사용자 이름
        access_token: JWT 액세스 토큰 (선택)
        role: 사용자 역할 (default: 'user')
    """
    session_manager.save_session(
        user_id=user_id,
        user_name=user_name,
        access_token=access_token or 'dummy_token',
        role=role
    )


def logout_user():
    """사용자 로그아웃 처리 및 세션 클리어"""
    session_manager.clear_session()


def require_auth(redirect_to_login: bool = True):
    """
    인증이 필요한 페이지에서 사용하는 데코레이터 함수

    Args:
        redirect_to_login: 로그인되지 않은 경우 로그인 페이지로 리다이렉트 여부

    Returns:
        bool: 로그인 여부
    """
    init_session_state()

    if not is_logged_in():
        if redirect_to_login:
            st.warning("⚠️ 로그인이 필요한 페이지입니다.")
            st.info("로그인 페이지로 이동합니다...")
            st.switch_page("pages/login.py")
        return False

    return True


def authenticate_with_backend(user_id: str, password: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    백엔드 API를 통한 사용자 인증

    Args:
        user_id: 사용자 ID
        password: 비밀번호

    Returns:
        Tuple[bool, Optional[dict], Optional[str]]:
            (인증 성공 여부, 사용자 정보, 에러 메시지)

    TODO: 실제 백엔드 API와 연동 필요
    """
    # 실제 구현 예시 (현재는 주석 처리)
    # try:
    #     import requests
    #     response = requests.post(
    #         "http://backend:8000/api/auth/login",
    #         json={"user_id": user_id, "password": password},
    #         timeout=5
    #     )
    #
    #     if response.status_code == 200:
    #         data = response.json()
    #         return True, {
    #             'user_id': data['user_id'],
    #             'user_name': data['name'],
    #             'role': data.get('role', 'user'),
    #             'access_token': data['access_token']
    #         }, None
    #     else:
    #         return False, None, "아이디 또는 비밀번호가 올바르지 않습니다."
    # except Exception as e:
    #     return False, None, f"서버 연결 오류: {str(e)}"

    # 임시 인증 로직 (모든 입력 허용)
    # 실제 운영 환경에서는 반드시 위의 백엔드 API 연동 코드로 교체해야 함
    if user_id and password:
        return True, {
            'user_id': user_id,
            'user_name': user_id,  # 실제로는 DB에서 이름 가져오기
            'role': 'user',  # 실제로는 DB에서 역할 가져오기
            'access_token': 'dummy_token'  # 실제로는 JWT 토큰
        }, None
    else:
        return False, None, "아이디와 비밀번호를 입력해주세요."


def register_user(user_id: str, password: str, email: str, name: str) -> Tuple[bool, Optional[str]]:
    """
    백엔드 API를 통한 사용자 등록

    Args:
        user_id: 사용자 ID
        password: 비밀번호
        email: 이메일
        name: 이름

    Returns:
        Tuple[bool, Optional[str]]: (등록 성공 여부, 에러 메시지)

    TODO: 실제 백엔드 API와 연동 필요
    """
    # 실제 구현 예시 (현재는 주석 처리)
    # try:
    #     import requests
    #     response = requests.post(
    #         "http://backend:8000/api/auth/signup",
    #         json={
    #             "user_id": user_id,
    #             "password": password,
    #             "email": email,
    #             "name": name
    #         },
    #         timeout=5
    #     )
    #
    #     if response.status_code == 201:
    #         return True, None
    #     else:
    #         data = response.json()
    #         return False, data.get('detail', '회원가입에 실패했습니다.')
    # except Exception as e:
    #     return False, f"서버 연결 오류: {str(e)}"

    # 임시 등록 로직 (항상 성공)
    # 실제 운영 환경에서는 반드시 위의 백엔드 API 연동 코드로 교체해야 함
    if user_id and password and email and name:
        return True, None
    else:
        return False, "모든 필드를 입력해주세요."


def get_auth_header() -> dict:
    """
    API 요청에 사용할 인증 헤더 반환

    Returns:
        dict: Authorization 헤더
    """
    user = get_current_user()
    if not user or not user.get('access_token'):
        return {}

    return {
        'Authorization': f'Bearer {user["access_token"]}'
    }


def get_session_info() -> dict:
    """
    현재 세션 정보 조회

    Returns:
        dict: 세션 정보 (로그인 시간, 활동 시간 등)
    """
    return session_manager.get_session_info()
