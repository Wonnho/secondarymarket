# header.py
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.auth import is_logged_in, get_current_user, logout_user

def render_header():
    """네비게이션 헤더를 렌더링하는 함수"""

    # CSS 스타일
    st.markdown("""
        <style>
        /* 사이드바 폭 조정 */
        [data-testid="stSidebar"] {
            min-width: 200px;
            max-width: 200px;
        }
        [data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 200px;
            max-width: 200px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            margin-left: -200px;
        }

        .header {
            background-color: #2c3e50;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-radius: 10px;
        }
        .header-left {
            display: flex;
            gap: 2rem;
            align-items: center;
        }
        .header-title {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0;
        }
        .header-menu {
            display: flex;
            gap: 1.5rem;
        }
        .nav-button {
            background: none;
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s;
        }
        .nav-button:hover {
            background-color: #34495e;
        }
        .header-right {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        .login-btn {
            background-color: #3498db;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        .login-btn:hover {
            background-color: #2980b9;
        }
        </style>
    """, unsafe_allow_html=True)

    # 헤더 컨텐츠
    col1, col2, col3, col4 = st.columns([2, 5, 1.5, 1])

    with col1:
        st.markdown('<div class="header-title">📈 KRX</div>', unsafe_allow_html=True)

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

    with col3:
        lang = st.selectbox(
            "언어",
            ["한국어", "English", "中文", "日本語"],
            label_visibility="collapsed",
            key="lang_select"
        )

    with col4:
        # 로그인 상태에 따라 다른 버튼 표시
        if is_logged_in():
            # 로그인된 경우: 사용자 정보와 로그아웃 버튼
            user = get_current_user()
            user_name = user['user_name'] if user else 'User'

            # 사용자 메뉴
            with st.popover(f"👤 {user_name}", use_container_width=True):
                st.markdown(f"**{user_name}님**")
                st.markdown(f"_{user['user_id']}_")
                st.markdown("---")
                if st.button("내 정보", key="profile", use_container_width=True):
                    st.info("내 정보 페이지 (준비중)")
                if st.button("설정", key="settings", use_container_width=True):
                    st.info("설정 페이지 (준비중)")
                st.markdown("---")
                if st.button("로그아웃", key="logout_btn", use_container_width=True, type="secondary"):
                    # 로그아웃 처리
                    logout_user()
                    st.success("로그아웃 되었습니다.")
                    st.rerun()
        else:
            # 로그인되지 않은 경우: 로그인 버튼
            if st.button("로그인", key="login_btn", use_container_width=True, type="primary"):
                st.switch_page("pages/login.py")