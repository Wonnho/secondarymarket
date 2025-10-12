import FinanceDataReader as fdr
import streamlit as st

from header import render_header  # ✅ 헤더 import

# 페이지 설정
st.set_page_config(page_title="주식 시장 현황", layout="wide")

# 헤더 렌더링
render_header()  # ✅ 헤더 함수 호출

# 제목 중앙 정렬
st.markdown("<h1 style='text-align: center;'>📈 한국 주식 시장</h1>", unsafe_allow_html=True)

# 간격 추가
st.write("")
st.write("")

# 한국거래소 상장종목 전체
df_krx = fdr.StockListing('KRX')

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

df_kospi_filtered = df_krx[df_krx['Market'] == 'KOSPI']
if "상위" in kospi_order:
    df_kospi = df_kospi_filtered.sort_values('Marcap', ascending=False).head(20)
else:
    df_kospi = df_kospi_filtered.sort_values('Marcap', ascending=True).head(20)

df_kospi_display = df_kospi[columns_to_show].rename(columns=columns_mapping)
st.dataframe(df_kospi_display, height=400, width=780, hide_index=True)

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

df_kosdaq_filtered = df_krx[df_krx['Market'] == 'KOSDAQ']
if "상위" in kosdaq_order:
    df_kosdaq = df_kosdaq_filtered.sort_values('Marcap', ascending=False).head(20)
else:
    df_kosdaq = df_kosdaq_filtered.sort_values('Marcap', ascending=True).head(20)

df_kosdaq_display = df_kosdaq[columns_to_show].rename(columns=columns_mapping)
st.dataframe(df_kosdaq_display, height=400, width=780, hide_index=True)

# 간격 추가
st.write("")
st.write("")
