import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Rebound Alert", layout="wide")
st.title("📈 RSI Rebound Scanner (Price Crosses RSI 30 Upward)")

st.sidebar.header("Scan Settings")
tickers = st.sidebar.text_area("Enter tickers (comma separated):", "AAPL,MSFT,TSLA,NVDA,GOOGL").split(',')
tickers = [t.strip().upper() for t in tickers if t.strip()]

lookback_days = st.sidebar.number_input("Days to look back for RSI < 30", min_value=5, max_value=30, value=14)

# RSI Function
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Signal Detection
def check_rsi_rebound(ticker):
    df = yf.download(ticker, interval="1d", period="60d", progress=False)
    if df.empty or len(df) < lookback_days:
        return None

    df['RSI'] = calculate_rsi(df)
    df = df.dropna()

    recent = df.iloc[-lookback_days:]
    below_30 = recent[recent['RSI'] < 30]

    if not below_30.empty:
        latest_close = float(df['Close'].dropna().values[-1])
        latest_rsi = float(df['RSI'].dropna().values[-1])
        if latest_close > latest_rsi:
            return {
                "Ticker": ticker,
                "Date": df.index[-1].date(),
                "Price": round(latest_close, 2),
                "RSI": round(latest_rsi, 2)
            }
    return None

if st.button("🚀 Run RSI Rebound Scan"):
    results = []
    for ticker in tickers:
        signal = check_rsi_rebound(ticker)
        if signal:
            results.append(signal)

    if results:
        df_out = pd.DataFrame(results)
        st.success(f"✅ Found {len(df_out)} ticker(s) where price > RSI after RSI < 30:")
        st.dataframe(df_out)
    else:
        st.info("No RSI rebound signals found today.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
