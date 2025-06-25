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
    df = yf.download(ticker, interval=interval, p
