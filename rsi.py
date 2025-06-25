import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Crossing EMA50 Scanner", layout="wide")
st.title("📈 RSI < 30 & RSI Crossing EMA50 (from below) Scanner")

st.sidebar.header("Scan Settings")

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

def check_rsi_cross_ema50(ticker):
    df = yf.download(ticker, interval=yf_interval, period=period, progress=False)
    if df.empty or len(df) < lookback_bars_needed:
        return None

    df['RSI'] = calculate_rsi(df)
    df['RSI_EMA50'] = df['RSI'].ewm(span=50, adjust=False).mean()
    df = df.dropna()

    latest_rsi = float(df['RSI'].iloc[-1])
    previous_rsi = float(df['RSI'].iloc[-2])
    latest_ema = float(df['RSI_EMA50'].iloc[-1])
    previous_ema = float(df['RSI_EMA50'].iloc[-2])

    crossed_above = (previous_rsi < previous_ema) and (latest_rsi > latest_ema) and (latest_rsi < 30)

    if crossed_above:
        latest_close = float(df['Close'].iloc[-1])
        return {
            "Ticker": ticker,
            "Date": df.index[-1].strftime("%Y-%m-%d %H:%M:%S"),
            "Price": round(latest_close, 2),
            "RSI": round(latest_rsi, 2),
            "RSI_EMA50": round(latest_ema, 2),
            "Interval": interval,
        }
    return None

if st.button("🚀 Run RSI < 30 & RSI crossing EMA50 scan"):
    results = []
    for ticker in tickers:
        signal = check_rsi_cross_ema50(ticker)
        if signal:
            results.append(signal)

    if results:
        df_out = pd.DataFrame(results)
        st.success(f"✅ Found {len(df_out)} ticker(s) matching condition:")
        st.dataframe(df_out)
    else:
        st.info("No tickers found with RSI < 30 crossing above EMA50 right now.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
