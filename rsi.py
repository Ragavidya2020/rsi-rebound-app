import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Rebound Scanner", layout="wide")
st.title("📈 RSI Rebound Scanner (RSI < 30 & Rising)")

# Sidebar options
st.sidebar.header("Settings")
tickers = st.sidebar.text_area("Enter tickers (comma separated):", "AAPL,MSFT,TSLA,NVDA,GOOGL,SRPT").split(',')
tickers = [t.strip().upper() for t in tickers if t.strip()]

interval = st.sidebar.selectbox("Interval", ["1d", "30m", "5m", "1m"], index=0)

# How much data to fetch based on interval
period_map = {
    "1d": "90d",
    "30m": "30d",
    "5m": "7d",
    "1m": "2d"
}
period = period_map[interval]

lookback_bars = st.sidebar.number_input("Lookback bars for RSI < 30", min_value=5, max_value=50, value=14)

# RSI Calculation
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Check for RSI rebound after going below 30
def check_rsi_rebound(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < lookback_bars + 2:
        st.write(f"🔴 {ticker}: Not enough data")
        return None

    df['RSI'] = calculate_rsi(df)
    df = df.dropna()

    rsi_series = df['RSI']
    recent = rsi_series.iloc[-lookback_bars:]

    # Find if RSI dropped below 30 and is now rising
    if (recent < 30).any():
        if rsi_series.iloc[-2] < rsi_series.iloc[-1]:
            latest = df.iloc[-1]
            return {
                "Ticker": ticker,
                "Time": latest.name.strftime("%Y-%m-%d %H:%M"),
                "Price": round(latest['Close'], 2),
                "RSI": round(rsi_series.iloc[-1], 2)
            }
    return None

if st.button("🚀 Run Scanner"):
    results = []
    for ticker in tickers:
        signal = check_rsi_rebound(ticker)
        if signal:
            results.append(signal)

    if results:
        df_out = pd.DataFrame(results)
        st.success(f"✅ Found {len(df_out)} RSI rebound(s):")
        st.dataframe(df_out)
    else:
        st.info("No RSI rebound signals found.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
