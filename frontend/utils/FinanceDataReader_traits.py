import FinanceDataReader as fdr

# 1. StockListing (상장 종목 리스트) 컬럼
print("=== KRX 상장 종목 컬럼 ===")
df_krx = fdr.StockListing('KRX')
print(df_krx.columns.tolist())
print("\n샘플 데이터:")
print(df_krx.head(3))

# 2. DataReader (주가 데이터) 컬럼
print("\n\n=== 주가 데이터 컬럼 (삼성전자) ===")
df_stock = fdr.DataReader('005930', '2024-01-01')
print(df_stock.columns.tolist())
print("\n샘플 데이터:")
print(df_stock.head(3))

# 3. 다른 시장 상장 종목 컬럼
print("\n\n=== KOSPI 상장 종목 컬럼 ===")
df_kospi = fdr.StockListing('KOSPI')
print(df_kospi.columns.tolist())

print("\n\n=== KOSDAQ 상장 종목 컬럼 ===")
df_kosdaq = fdr.StockListing('KOSDAQ')
print(df_kosdaq.columns.tolist())

# 4. 미국 주식 데이터 컬럼
print("\n\n=== 미국 주식 데이터 컬럼 (애플) ===")
df_us = fdr.DataReader('AAPL', '2024-01-01')
print(df_us.columns.tolist())