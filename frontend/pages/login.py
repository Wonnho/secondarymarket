# pages/login.py
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from components.header import render_header

# 페이지 설정
st.set_page_config(page_title="로그인", layout="wide")

# 헤더 렌더링
render_header()

# 로그인 폼 중앙 정렬
st.markdown("<h1 style='text-align: center; margin-top: 2rem;'>🔐 로그인</h1>", unsafe_allow_html=True)

# 중앙 정렬을 위한 컬럼
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("")
    st.write("")
    
    # 로그인 폼
    with st.form("login_form"):
        st.markdown("### 로그인 정보 입력")
        
        # 아이디 입력
        user_id = st.text_input("아이디", placeholder="아이디를 입력하세요")
        
        # 비밀번호 입력
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        
        st.write("")
        
        # 로그인 버튼
        submit_button = st.form_submit_button("로그인", use_container_width=True, type="primary")
        
        if submit_button:
            if user_id and password:
                # 여기에 실제 로그인 로직 추가
                # 예: 데이터베이스 확인, 세션 저장 등
                st.success(f"환영합니다, {user_id}님!")
                st.balloons()
                # 로그인 성공 후 메인 페이지로 이동
                # st.switch_page("finance.py")
            else:
                st.error("아이디와 비밀번호를 모두 입력해주세요.")
    
    st.write("")
    st.write("")
    
    # 회원가입 링크
    st.markdown("---")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("##### 계정이 없으신가요?")
    with col_b:
        if st.button("회원가입", use_container_width=True):
            st.switch_page("pages/signup.py")
    
    # 추가 옵션
    st.write("")
    col_x, col_y = st.columns(2)
    with col_x:
        st.checkbox("로그인 상태 유지")
    with col_y:
        st.markdown("[비밀번호 찾기](#)")