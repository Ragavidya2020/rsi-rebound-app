import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Rebound + EMA50 Crossover Scanner", layout="wide")
st.title("📈 RSI Rebound (RSI < 30 then crosses EMA50) Scanner")

st.sidebar.header("Scan Settings")

# Default large ticker list (Tech, Healthcare, Financials, Industrials, Consumer Disc)
tickers = [
    # Technology
    "AAPL", "MSFT", "NVDA", "AVGO", "ADBE", "CRM", "INTC", "AMD", "QCOM", "CSCO",
    "ORCL", "TXN", "MU", "AMAT", "NOW", "PANW", "IBM", "KLAC", "SNPS", "WDAY",
    # Healthcare
    "JNJ", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT", "AMGN", "CVS", "ISRG",
    "CI", "HCA", "GILD", "VRTX", "BMY", "BDX", "ZBH", "EW", "REGN", "ALGN",
    # Financials
    "JPM", "BAC", "WFC", "C", "GS", "MS", "AXP", "SCHW", "SPGI", "BLK",
    "AIG", "CB", "ICE", "MMC", "COF", "MTB", "TFC", "ALL", "PGR", "FITB",
    # Industrials
    "HON", "GE", "UPS", "CAT", "DE", "LMT", "RTX", "BA", "ETN", "NOC",
    "EMR", "UNP", "GD", "PH", "ROK", "IR", "AME", "FAST", "PCAR", "TXT",
    # Consumer Discretionary
    "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "BKNG", "TGT", "ROST", "F",
    "GM", "EBAY", "MAR", "YUM", "DPZ", "AZO", "ORLY", "ULTA", "DHI", "LEN"
]

tickers_input = st.sidebar.text_area("Tickers (comma separated, optional):", "")
if tickers_input.strip():
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

interval = st.sidebar.selectbox(
    "Select Interval for RSI & EMA calculation",
    options=["1m", "5m", "30m", "60m", "120m", "1d", "4h"],
    index=5,
)

interval_map = {
    "1m": "1m",
    "5m": "5m",
    "30m": "30m",
    "60m": "60m",
    "120m": "120m",
    "1d": "1d",
    "4h": "240m",
}
yf_interval = interval_map.get(interval, "1d")

period = "60d" if yf_interval.endswith("m") else "180d"
lookback_bars_needed = 60

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def check_rsi_rebound_cross(ticker):
    df = yf.download(ticker, interval=yf_interval, period=period, progress=False)
    if df.empty or len(df) < lookback_bars_needed:
        return None

    df['RSI'] = calculate_rsi(df)
    df['RSI_EMA50'] = df['RSI'].ewm(span=50, adjust=False).mean()
    df = df.dropna()

    # Need at least 3 bars to check condition
    if len(df) < 3:
        return None

    rsi_3ago = df['RSI'].iloc[-3]
    rsi_2ago = df['RSI'].iloc[-2]
    rsi_1ago = df['RSI'].iloc[-1]

    ema_3ago = df['RSI_EMA50'].iloc[-3]
    ema_2ago = df['RSI_EMA50'].iloc[-2]
    ema_1ago = df['RSI_EMA50'].iloc[-1]

    # Condition: RSI was <30 three bars ago,
    # RSI was below EMA50 2 bars ago,
    # RSI crosses EMA50 from below on last bar
    crossed_above = (rsi_3ago < 30) and (rsi_2ago < ema_2ago) and (rsi_1ago > ema_1ago)

    if crossed_above:
        latest_close = float(df['Close'].iloc[-1])
        return {
            "Ticker": ticker,
            "Date": df.index[-1].strftime("%Y-%m-%d %H:%M:%S"),
            "Price": round(latest_close, 2),
            "RSI": round(rsi_1ago, 2),
            "RSI_EMA50": round(ema_1ago, 2),
            "Interval": interval,
        }
    return None

if st.button("🚀 Run RSI Rebound + EMA50 Crossover Scan"):
    results = []
    for ticker in tickers:
        signal = check_rsi_rebound_cross(ticker)
        if signal:
            results.append(signal)

    if results:
        df_out = pd.DataFrame(results)
        st.success(f"✅ Found {len(df_out)} ticker(s) matching RSI rebound + EMA50 crossover:")
        st.dataframe(df_out)
    else:
        st.info("No tickers found with RSI rebound crossing EMA50 at this time.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
