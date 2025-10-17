import FinanceDataReader as fdr
import streamlit as st
from datetime import datetime, time, timedelta
import pandas as pd

from components.header import render_header  # ✅ 헤더 import

# 페이지 설정
st.set_page_config(page_title="주식 시장 현황", layout="wide")

# 헤더 렌더링
render_header()  # ✅ 헤더 함수 호출

# 제목 중앙 정렬
st.markdown("<h1 style='text-align: center;'>📈 한국 주식 시장</h1>", unsafe_allow_html=True)

# 간격 추가
st.write("")
st.write("")


@st.cache_data(ttl=300)  # 5분 캐시
def load_market_data_with_fallback():
    """
    시장 데이터 로드 (9시 이전에는 전날 종가 데이터 사용)

    Returns:
        pd.DataFrame: 시장 데이터
    """
    now = datetime.now()
    market_open_time = time(9, 0)  # 오전 9시

    try:
        # 기본 상장 종목 데이터 로드
        df_krx = fdr.StockListing('KRX')

        # 9시 이전이거나 현재가가 없는 경우
        if now.time() < market_open_time or df_krx['Close'].isna().any():
            st.info("🕘 장 시작 전입니다. 전일 종가 기준으로 표시됩니다.")

            # 전날 거래일 계산 (주말 고려)
            previous_trading_day = now - timedelta(days=1)

            # 토요일(5)이면 금요일로, 일요일(6)이면 금요일로
            if previous_trading_day.weekday() == 5:  # 토요일
                previous_trading_day -= timedelta(days=1)
            elif previous_trading_day.weekday() == 6:  # 일요일
                previous_trading_day -= timedelta(days=2)

            # 각 종목의 전일 종가 데이터 가져오기 (상위 100개만)
            # 실시간 데이터가 없으면 전날 데이터 사용
            for idx in df_krx.head(100).index:
                if pd.isna(df_krx.loc[idx, 'Close']):
                    ticker = df_krx.loc[idx, 'Code']
                    try:
                        # 최근 2일 데이터 가져오기
                        hist_data = fdr.DataReader(
                            ticker,
                            start=(previous_trading_day - timedelta(days=5)).strftime('%Y-%m-%d'),
                            end=previous_trading_day.strftime('%Y-%m-%d')
                        )

                        if not hist_data.empty:
                            last_close = hist_data['Close'].iloc[-1]
                            df_krx.loc[idx, 'Close'] = last_close

                            # Open, High, Low도 전날 데이터 사용
                            df_krx.loc[idx, 'Open'] = hist_data['Open'].iloc[-1]
                            df_krx.loc[idx, 'High'] = hist_data['High'].iloc[-1]
                            df_krx.loc[idx, 'Low'] = hist_data['Low'].iloc[-1]
                    except Exception as e:
                        # 개별 종목 오류는 무시하고 계속 진행
                        continue

        return df_krx

    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        # 빈 데이터프레임 반환
        return pd.DataFrame()


# 한국거래소 상장종목 전체 (캐시 적용)
df_krx = load_market_data_with_fallback()

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

    df_kospi_display = df_kospi[columns_to_show].rename(columns=columns_mapping)
    st.dataframe(df_kospi_display, height=400, width=780, hide_index=True)
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

    df_kosdaq_display = df_kosdaq[columns_to_show].rename(columns=columns_mapping)
    st.dataframe(df_kosdaq_display, height=400, width=780, hide_index=True)
else:
    st.warning("KOSDAQ 데이터를 불러올 수 없습니다.")

# 간격 추가
st.write("")
st.write("")
