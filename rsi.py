import streamlit as st
import yfinance as yf
import pandas as pd

st.title("RSI and EMA50 Debug Scanner")

tickers = [
    "AAPL", "TSLA", "MSFT", "NVDA", "AMD"
]

interval = st.selectbox("Select interval", options=["1d", "30m", "5m"], index=0)
period = "180d" if interval == "1d" else "60d"

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

st.write(f"Fetching {interval} data for tickers...")

for ticker in tickers:
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 20:
        st.write(f"{ticker}: No data or too little data")
        continue

    df['RSI'] = calculate_rsi(df)
    df['RSI_EMA50'] = df['RSI'].ewm(span=50, adjust=False).mean()
    df = df.dropna()

    latest_rsi = df['RSI'].iloc[-1]
    latest_ema = df['RSI_EMA50'].iloc[-1]

    st.write(f"{ticker}: RSI = {latest_rsi:.2f}, RSI_EMA50 = {latest_ema:.2f}")
