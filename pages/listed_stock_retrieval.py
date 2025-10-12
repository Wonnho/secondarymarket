import streamlit as st
from header import render_header
import sys

sys.path.append('..')
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="상장종목조회",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_header()

st.title("📊 상장종목조회")

# KRX 전체 종목 로드
@st.cache_data
def load_krx_data():
    return fdr.StockListing('KRX')

df_krx = load_krx_data()

# 색상 변경 함수
def color_change(val):
    if val > 0:
        color = 'red'
    elif val < 0:
        color = 'blue'
    else:
        color = 'black'
    return f'color: {color}'

# 입력 폼
col1, col2 = st.columns([3, 1])

with col1:
    stock_name = st.text_input("종목명 입력", value="삼성전자", key="stock_name")

with col2:
    start_year = st.text_input("시작 연도", value="2014", key="start_year")

if st.button("조회", key="btn_by_name", type="primary"):
    matched = df_krx[df_krx['Name'] == stock_name]
    
    if matched.empty:
        st.error(f"'{stock_name}' 종목을 찾을 수 없습니다.")
    else:
        ticker = matched.iloc[0]['Code']
        st.info(f"종목코드: {ticker}")
        
        with st.spinner(f"{stock_name} 데이터를 불러오는 중..."):
            try:
                df = fdr.DataReader(ticker, start_year)
                
                # 컬럼명 매핑
                price_columns_mapping = {
                    'Open': '시가',
                    'High': '고가',
                    'Low': '저가',
                    'Close': '종가',
                    'Volume': '거래량',
                    'Change': '전일대비'
                }
                
                # 데이터 정렬 및 컬럼명 변경
                df_sorted = df.sort_index(ascending=False)
                df_sorted_renamed = df_sorted.rename(columns=price_columns_mapping)
                
                # 스타일 적용
                styled_df = df_sorted_renamed.style.applymap(
                    color_change, 
                    subset=['전일대비']
                )
                
                # 결과 표시
                st.subheader(f"{stock_name} ({ticker}) 종목 데이터")
                st.dataframe(styled_df, use_container_width=True, hide_index=False)
                
                # 차트 표시
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.subheader("종가 차트")
                    st.line_chart(df_sorted['Close'])
                
                with col_chart2:
                    st.subheader("거래량 차트")
                    st.line_chart(df_sorted['Volume'])
                
                # 최근 52주(1년) 데이터 필터링
                today = datetime.now()
                one_year_ago = today - timedelta(weeks=52)
                
                # 인덱스가 datetime인지 확인하고 필터링
                if isinstance(df_sorted.index[0], pd.Timestamp):
                    df_52weeks = df_sorted[df_sorted.index >= one_year_ago]
                else:
                    # 인덱스를 datetime으로 변환
                    df_sorted.index = pd.to_datetime(df_sorted.index)
                    df_52weeks = df_sorted[df_sorted.index >= one_year_ago]
                
                # 52주 통계 정보
                st.subheader("📈 52주 통계 정보")
                
                if len(df_52weeks) > 0:
                    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                    
                    week_52_high = df_52weeks['Close'].max()
                    week_52_low = df_52weeks['Close'].min()
                    week_52_avg = df_52weeks['Close'].mean()
                    current_price = df_52weeks['Close'].iloc[0]
                    
                    # 52주 최고가 대비 현재가 비율
                    high_ratio = ((current_price - week_52_high) / week_52_high * 100)
                    # 52주 최저가 대비 현재가 비율
                    low_ratio = ((current_price - week_52_low) / week_52_low * 100)
                    
                    with stat_col1:
                        st.metric(
                            "최고가", 
                            f"{week_52_high:,.0f}원",
                            f"{high_ratio:+.2f}%"
                        )
                    
                    with stat_col2:
                        st.metric(
                            "최저가", 
                            f"{week_52_low:,.0f}원",
                            f"{low_ratio:+.2f}%"
                        )
                    
                    with stat_col3:
                        avg_diff = current_price - week_52_avg
                        avg_ratio = (avg_diff / week_52_avg * 100)
                        st.metric(
                            "평균가", 
                            f"{week_52_avg:,.0f}원",
                            f"{avg_ratio:+.2f}%"
                        )
                    
                    with stat_col4:
                        # 1년 전 가격과 비교
                        first_price = df_52weeks['Close'].iloc[-1]
                        price_change = current_price - first_price
                        price_change_ratio = (price_change / first_price * 100)
                        
                        st.metric(
                            "현재가", 
                            f"{current_price:,.0f}원",
                            f"{price_change:+,.0f}원 ({price_change_ratio:+.2f}%)"
                        )
                    
                    # 추가 정보
                    st.info(f"""
                    **52주 데이터 기간:** {df_52weeks.index[-1].strftime('%Y-%m-%d')} ~ {df_52weeks.index[0].strftime('%Y-%m-%d')}  
                    **데이터 개수:** {len(df_52weeks)}일  
                    **52주 최고가 달성일:** {df_52weeks['Close'].idxmax().strftime('%Y-%m-%d')}  
                    **52주 최저가 달성일:** {df_52weeks['Close'].idxmin().strftime('%Y-%m-%d')}
                    """)
                    
                else:
                    st.warning("52주 데이터가 충분하지 않습니다.")
                    
            except Exception as e:
                st.error(f"데이터 조회 중 오류가 발생했습니다: {str(e)}")
