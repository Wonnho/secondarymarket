import FinanceDataReader as fdr
import streamlit as st
from datetime import datetime, time, timedelta
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from components.header import render_header
from utils.auth import init_session_state

# 페이지 설정
st.set_page_config(page_title="주식 시장 현황", layout="wide")

# 세션 상태 초기화 (로그인 상태 유지를 위해 필수!)
init_session_state()

# 헤더 렌더링
render_header()

# 제목 중앙 정렬
st.markdown("<h1 style='text-align: center;'>📈 한국 주식 시장</h1>", unsafe_allow_html=True)

# 간격 추가
st.write("")
st.write("")


# 색상 변경 함수 (상승=빨강, 하락=파랑)
def color_change(val):
    """
    등락률에 따라 색상 적용

    Args:
        val: 등락률 값

    Returns:
        str: CSS 색상 스타일
    """
    if pd.isna(val):
        return 'color: black'
    if val > 0:
        return 'color: red; font-weight: bold'
    elif val < 0:
        return 'color: blue; font-weight: bold'
    else:
        return 'color: black'


@st.cache_data(ttl=300)  # 5분 캐시
def load_market_data():
    """
    시장 데이터 로드
    - 오전 9시 이전: 전일 종가 데이터 (KOSPI/KOSDAQ 전체)
    - 오전 9시 이후: 실시간 데이터

    Returns:
        pd.DataFrame: 시장 데이터
    """
    now = datetime.now()
    market_open_time = time(9, 0)  # 오전 9시
    is_pre_market = now.time() < market_open_time

    try:
        # 9시 이전: 전일 종가 데이터 로드
        if is_pre_market:
            # KOSPI 전체 데이터
            df_kospi_stock = fdr.StockListing('KOSPI')
            # KOSDAQ 전체 데이터
            df_kosdaq_stock = fdr.StockListing('KOSDAQ')
            # 두 데이터 합치기
            df_krx = pd.concat([df_kospi_stock, df_kosdaq_stock], ignore_index=True)
        else:
            # 9시 이후: 실시간 데이터
            df_krx = fdr.StockListing('KRX')

        return df_krx

    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        return pd.DataFrame()


# 한국거래소 상장종목 전체 (캐시 적용)
df_krx = load_market_data()

# 표시할 컬럼 선택 및 한글 컬럼명 매핑
columns_to_show = ['Name', 'Close', 'ChagesRatio', 'Open', 'Low', 'High']
columns_mapping = {
    'Name': '종목명',
    'Close': '현재가',
    'ChagesRatio': '등락률(%)',
    'Open': '시가',
    'Low': '저가',
    'High': '고가'
}

# KOSPI 섹션
col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("📊 KOSPI 상장 종목")
with col2:
    kospi_order = st.radio(
        "정렬",
        ["시가총액 상위 20", "시가총액 하위 20"],
        key="kospi_order",
        horizontal=True,
        label_visibility="collapsed"
    )

if not df_krx.empty:
    df_kospi_filtered = df_krx[df_krx['Market'] == 'KOSPI']
    if "상위" in kospi_order:
        df_kospi = df_kospi_filtered.sort_values('Marcap', ascending=False).head(20)
    else:
        df_kospi = df_kospi_filtered.sort_values('Marcap', ascending=True).head(20)

    # 데이터프레임 준비 및 컬럼명 변경
    df_kospi_display = df_kospi[columns_to_show].rename(columns=columns_mapping)

    # 스타일 적용: 등락률 컬럼에 색상 적용
    styled_kospi = df_kospi_display.style.applymap(
        color_change,
        subset=['등락률(%)']
    )

    # 스타일 적용된 데이터프레임 표시
    st.dataframe(styled_kospi, height=400, use_container_width=True, hide_index=True)
else:
    st.warning("KOSPI 데이터를 불러올 수 없습니다.")

# 간격 추가
st.write("")

# KOSDAQ 섹션
col3, col4 = st.columns([3, 2])
with col3:
    st.subheader("📊 KOSDAQ 상장 종목")
with col4:
    kosdaq_order = st.radio(
        "정렬",
        ["시가총액 상위 20", "시가총액 하위 20"],
        key="kosdaq_order",
        horizontal=True,
        label_visibility="collapsed"
    )

if not df_krx.empty:
    df_kosdaq_filtered = df_krx[df_krx['Market'] == 'KOSDAQ']
    if "상위" in kosdaq_order:
        df_kosdaq = df_kosdaq_filtered.sort_values('Marcap', ascending=False).head(20)
    else:
        df_kosdaq = df_kosdaq_filtered.sort_values('Marcap', ascending=True).head(20)

    # 데이터프레임 준비 및 컬럼명 변경
    df_kosdaq_display = df_kosdaq[columns_to_show].rename(columns=columns_mapping)

    # 스타일 적용: 등락률 컬럼에 색상 적용
    styled_kosdaq = df_kosdaq_display.style.applymap(
        color_change,
        subset=['등락률(%)']
    )

    # 스타일 적용된 데이터프레임 표시
    st.dataframe(styled_kosdaq, height=400, use_container_width=True, hide_index=True)
else:
    st.warning("KOSDAQ 데이터를 불러올 수 없습니다.")

# 간격 추가
st.write("")
st.write("")
