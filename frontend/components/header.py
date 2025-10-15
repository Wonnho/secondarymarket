# header.py
import streamlit as st

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
        if st.button("로그인", key="login_btn", use_container_width=True, type="primary"):
            st.switch_page("pages/login.py")  # ✅ 로그인 페이지로 이동