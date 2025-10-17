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
def get_previous_trading_day():
    """
    이전 거래일 계산 (주말 및 공휴일 고려)

    Returns:
        datetime: 이전 거래일
    """
    now = datetime.now()
    previous_day = now - timedelta(days=1)

    # 토요일(5)이면 금요일로
    if previous_day.weekday() == 5:
        previous_day -= timedelta(days=1)
    # 일요일(6)이면 금요일로
    elif previous_day.weekday() == 6:
        previous_day -= timedelta(days=2)

    return previous_day


@st.cache_data(ttl=300)  # 5분 캐시
def load_market_data_with_fallback():
    """
    시장 데이터 로드 (9시 이전에는 전날 종가 데이터 사용)
    전체 KOSPI/KOSDAQ 종목의 데이터를 효율적으로 로드

    Returns:
        pd.DataFrame: 시장 데이터
    """
    now = datetime.now()
    market_open_time = time(9, 0)  # 오전 9시
    is_pre_market = now.time() < market_open_time

    try:
        # 기본 상장 종목 리스트 로드
        df_krx = fdr.StockListing('KRX')

        # 9시 이전이거나 현재가 데이터가 대부분 없는 경우
        missing_data_count = df_krx['Close'].isna().sum()

        if is_pre_market or missing_data_count > 100:
            st.info("🕘 장 시작 전입니다. 전일 종가 기준으로 표시됩니다.")

            # 이전 거래일 계산
            previous_trading_day = get_previous_trading_day()

            # KOSPI/KOSDAQ 시장 전체 데이터를 한번에 가져오기 (훨씬 빠름)
            try:
                # KOSPI 전체 데이터 로드 (종목별로 하나씩이 아닌 시장 전체)
                st.info("📊 KOSPI 전체 종목 데이터 로딩 중...")
                df_kospi_stock = fdr.StockListing('KOSPI')

                # KOSDAQ 전체 데이터 로드
                st.info("📊 KOSDAQ 전체 종목 데이터 로딩 중...")
                df_kosdaq_stock = fdr.StockListing('KOSDAQ')

                # 두 데이터 합치기
                df_market = pd.concat([df_kospi_stock, df_kosdaq_stock], ignore_index=True)

                # 기존 df_krx의 Code를 키로 병합
                # df_market에 있는 Close, Open, High, Low 데이터를 df_krx에 업데이트
                df_krx = df_krx.set_index('Code')
                df_market = df_market.set_index('Code')

                # Close, Open, High, Low, Volume, ChagesRatio 업데이트
                for col in ['Close', 'Open', 'High', 'Low', 'Volume', 'ChagesRatio']:
                    if col in df_market.columns:
                        df_krx[col] = df_market[col].combine_first(df_krx[col])

                df_krx = df_krx.reset_index()

                st.success(f'✅ 전체 {len(df_krx)}개 종목 데이터 로드 완료!')

            except Exception as e:
                st.warning(f"시장 전체 데이터 로드 실패: {str(e)}")
                st.info("개별 종목 데이터를 로드합니다... (시간이 소요될 수 있습니다)")

                # 대체 방법: 표시할 상위 종목만 로드 (시가총액 상위/하위 각 50개)
                df_krx = df_krx.sort_values('Marcap', ascending=False)

                # KOSPI 상위 50개 + 하위 50개
                kospi_stocks = df_krx[df_krx['Market'] == 'KOSPI']
                kospi_top = kospi_stocks.head(50)
                kospi_bottom = kospi_stocks.tail(50)

                # KOSDAQ 상위 50개 + 하위 50개
                kosdaq_stocks = df_krx[df_krx['Market'] == 'KOSDAQ']
                kosdaq_top = kosdaq_stocks.head(50)
                kosdaq_bottom = kosdaq_stocks.tail(50)

                # 로드할 종목 리스트
                stocks_to_load = pd.concat([kospi_top, kospi_bottom, kosdaq_top, kosdaq_bottom])

                # 이전 거래일 데이터 로드
                start_date = (previous_trading_day - timedelta(days=5)).strftime('%Y-%m-%d')
                end_date = previous_trading_day.strftime('%Y-%m-%d')

                progress_bar = st.progress(0)
                status_text = st.empty()
                total = len(stocks_to_load)

                for i, (idx, row) in enumerate(stocks_to_load.iterrows()):
                    ticker = row['Code']

                    try:
                        hist_data = fdr.DataReader(ticker, start=start_date, end=end_date)

                        if not hist_data.empty:
                            last_row = hist_data.iloc[-1]

                            # 데이터 업데이트
                            df_krx.loc[idx, 'Close'] = last_row['Close']
                            df_krx.loc[idx, 'Open'] = last_row['Open']
                            df_krx.loc[idx, 'High'] = last_row['High']
                            df_krx.loc[idx, 'Low'] = last_row['Low']

                            # 전일대비 계산
                            if len(hist_data) >= 2:
                                prev_close = hist_data.iloc[-2]['Close']
                                current_close = last_row['Close']
                                change_ratio = ((current_close - prev_close) / prev_close) * 100
                                df_krx.loc[idx, 'ChagesRatio'] = change_ratio

                    except Exception:
                        pass

                    # 진행률 업데이트
                    if (i + 1) % 10 == 0 or (i + 1) == total:
                        progress = (i + 1) / total
                        progress_bar.progress(progress)
                        status_text.text(f'처리 중: {i+1}/{total} 종목 ({progress*100:.1f}%)')

                progress_bar.empty()
                status_text.empty()
                st.success(f'✅ 주요 {total}개 종목 데이터 로드 완료!')

        return df_krx

    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
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
