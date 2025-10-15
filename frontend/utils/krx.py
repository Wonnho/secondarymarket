import FinanceDataReader as fdr
import streamlit as st

st.title("📈 한국 주식 데이터 조회")

# 한국거래소 상장종목 전체
df_krx = fdr.StockListing('KRX')

st.subheader("KRX 상장 종목")
st.dataframe(df_krx.head(20), height=400, width=780)


# 종목 선택
ticker = st.text_input("종목 코드 입력", value="068270")
start_year = st.text_input("시작 연도", value="2017")

if st.button("조회"):
    df = fdr.DataReader(ticker, start_year)
    
    st.subheader(f"{ticker} 종목 데이터")
    st.dataframe(df)
    
    st.subheader("종가 차트")
    st.line_chart(df['Close'])
