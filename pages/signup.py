# pages/signup.py
import streamlit as st
from header import render_header

# 페이지 설정
st.set_page_config(page_title="회원가입", layout="wide")

# 세션 상태 초기화
if 'signup_success' not in st.session_state:
    st.session_state.signup_success = False

# 회원가입 성공 시 로그인 페이지로 이동
if st.session_state.signup_success:
    st.session_state.signup_success = False  # 플래그 리셋
    st.switch_page("pages/login.py")

# 헤더 렌더링
render_header()

# 회원가입 폼 중앙 정렬
st.markdown("<h1 style='text-align: center; margin-top: 2rem;'>✍️ 회원가입</h1>", unsafe_allow_html=True)

# 중앙 정렬을 위한 컬럼
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("")
    st.write("")
    
    # 회원가입 폼
    with st.form("signup_form"):
        st.markdown("### 회원 정보 입력")
        
        # 아이디 입력
        user_id = st.text_input("아이디", placeholder="사용할 아이디를 입력하세요")
        
        # 비밀번호 입력
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        
        # 비밀번호 확인
        password_confirm = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요")
        
        # 이메일 입력
        email = st.text_input("이메일", placeholder="example@email.com")
        
        # 이름 입력
        name = st.text_input("이름", placeholder="이름을 입력하세요")
        
        st.write("")
        
        # 약관 동의
        agree = st.checkbox("이용약관 및 개인정보처리방침에 동의합니다")
        
        st.write("")
        
        # 회원가입 버튼
        submit_button = st.form_submit_button("회원가입", use_container_width=True, type="primary")
        
        if submit_button:
            if not all([user_id, password, password_confirm, email, name]):
                st.error("모든 필드를 입력해주세요.")
            elif password != password_confirm:
                st.error("비밀번호가 일치하지 않습니다.")
            elif not agree:
                st.error("이용약관에 동의해주세요.")
            else:
                # 여기에 실제 회원가입 로직 추가
                # 예: 데이터베이스에 사용자 정보 저장
                
                st.success("회원가입이 완료되었습니다!")
                st.balloons()
                
                # ✅ 세션 상태 업데이트 후 페이지 리로드
                st.session_state.signup_success = True
                st.rerun()
    
    st.write("")
    st.write("")
    
    # 로그인 링크
    st.markdown("---")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("##### 이미 계정이 있으신가요?")
    with col_b:
        if st.button("로그인", use_container_width=True):
            st.switch_page("pages/login.py")