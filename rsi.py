import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Rebound Alert", layout="wide")
st.title("📈 RSI Rebound Scanner (RSI < 30 and Price Crosses EMA50 Upward)")

st.sidebar.header("Scan Settings")

# Sample 100 tickers (20 each from 5 large sectors with market cap > $900M)
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
    tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

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
def check_rsi_ema50_cross(ticker):
    df = yf.download(ticker, interval="1d", period="60d", progress=False)
    if df.empty or len(df) < 51:
        return None

    df['RSI'] = calculate_rsi(df)
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df = df.dropna()

    latest_close = float(df['Close'].iloc[-1])
    previous_close = float(df['Close'].iloc[-2])
    latest_ema = float(df['EMA50'].iloc[-1])
    previous_ema = float(df['EMA50'].iloc[-2])
    latest_rsi = float(df['RSI'].iloc[-1])

    # Condition: RSI < 30 and price crosses EMA50 from below
    crossed_above = previous_close < previous_ema and latest_close > latest_ema
    if latest_rsi < 30 and crossed_above:
        return {
            "Ticker": ticker,
            "Date": df.index[-1].date(),
            "Price": round(latest_close, 2),
            "RSI": round(latest_rsi, 2),
            "EMA50": round(latest_ema, 2)
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
        st.info("No RSI + EMA50 crossover signals found today.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
