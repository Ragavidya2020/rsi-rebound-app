import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI + EMA50 Crossover Scanner", layout="wide")
st.title("📈 RSI < 30 & Price Crossing EMA50 Scanner with Interval Options")

st.sidebar.header("Scan Settings")

# 100+ tickers from 5 large sectors (Tech, Healthcare, Financials, Industrials, Consumer Disc)
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
    index=5,  # Default to 1d
)

# yfinance interval map
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

def check_rsi_ema50_cross(ticker):
    df = yf.download(ticker, interval=yf_interval, period=period, progress=False)
    if df.empty or len(df) < lookback_bars_needed:
        return None

    df['RSI'] = calculate_rsi(df)
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df = df.dropna()

    latest_close = float(df['Close'].iloc[-1])
    previous_close = float(df['Close'].iloc[-2])
    latest_ema = float(df['EMA50'].iloc[-1])
    previous_ema = float(df['EMA50'].iloc[-2])
    latest_rsi = float(df['RSI'].iloc[-1])

    crossed_above = previous_close < previous_ema and latest_close > latest_ema
    if latest_rsi < 30 and crossed_above:
        return {
            "Ticker": ticker,
            "Date": df.index[-1],
            "Price": round(latest_close, 2),
            "RSI": round(latest_rsi, 2),
            "EMA50": round(latest_ema, 2),
            "Interval": interval,
        }
    return None

if st.button("🚀 Run RSI + EMA50 Crossover Scan"):
    results = []
    for ticker in tickers:
        signal = check_rsi_ema50_cross(ticker)
        if signal:
            results.append(signal)

    if results:
        df_out = pd.DataFrame(results)
        st.success(f"✅ Found {len(df_out)} ticker(s) with RSI < 30 and price crossing above EMA50:")
        st.dataframe(df_out)
    else:
        st.info("No RSI + EMA50 crossover signals found at this interval.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
