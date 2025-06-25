import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Rebound + EMA50 Crossover", layout="wide")
st.title("📊 RSI Rebound & EMA50 Crossover Scanner")

# Sidebar controls
st.sidebar.header("Scan Settings")
tickers = st.sidebar.text_area("Enter tickers (comma separated):", "AAPL,MSFT,TSLA,NVDA,GOOGL,SRPT").split(',')
tickers = [t.strip().upper() for t in tickers if t.strip()]

interval = st.sidebar.selectbox("Select Time Interval", ["1d", "30m", "5m", "1m"], index=0)

# Period per interval
period_map = {
    "1d": "90d",
    "30m": "30d",
    "5m": "7d",
    "1m": "2d"
}
period = period_map[interval]

lookback_bars = st.sidebar.number_input("Bars to look back for RSI < 30", min_value=5, max_value=50, value=14)

# RSI Calculation
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Signal detection logic
def check_rsi_ema_rebound(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < lookback_bars + 2:
        return None

    df['RSI'] = calculate_rsi(df)
    df['RSI_EMA50'] = df['RSI'].ewm(span=50, adjust=False).mean()
    df = df.dropna()

    recent = df.iloc[-lookback_bars:]
    below_30 = recent[recent['RSI'] < 30]

    if not below_30.empty:
        # Check for crossover now
        rsi_prev = df['RSI'].iloc[-2]
        rsi_now = df['RSI'].iloc[-1]
        ema_prev = df['RSI_EMA50'].iloc[-2]
        ema_now = df['RSI_EMA50'].iloc[-1]

        if rsi_prev < ema_prev and rsi_now > ema_now:
            latest = df.iloc[-1]
            return {
                "Ticker": ticker,
                "Time": latest.name.strftime("%Y-%m-%d %H:%M"),
                "Price": round(latest['Close'], 2),
                "RSI": round(rsi_now, 2),
