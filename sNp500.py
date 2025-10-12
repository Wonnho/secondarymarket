import FinanceDataReader as fdr


# S&P 500 종목 전체
df_spx = fdr.StockListing('S&P500')
print(df_spx.head())