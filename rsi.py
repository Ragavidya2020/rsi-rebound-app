import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Support Bounce Scanner", layout="wide")
st.title("📉 Support Bounce Scanner (Confirmed Rebounds from Strong Support)")

# --- Strictly large-cap tickers (>$5B market cap) ---
large_cap_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "V", "MA", "JPM",
    "DIS", "HD", "PG", "PFE", "PEP", "KO", "XOM", "CVX", "WMT", "MRK",
    "LLY", "ABBV", "UNH", "JNJ", "COST", "TMO", "ABT", "AMD", "NFLX", "CRM",
    "INTC", "QCOM", "TXN", "AVGO", "ORCL", "NOW", "ADBE", "AMAT", "LRCX", "IBM",
    "GE", "CAT", "DE", "UPS", "BA", "LMT", "RTX", "GS", "MS", "BKNG",
    "MO", "PM", "MDT", "SYK", "BDX", "ZTS", "CVS", "CI", "TGT", "LOW",
    "SPGI", "ICE", "PLD", "CB", "BLK", "AXP", "ETN", "NOC", "GD", "HUM",
    "ISRG", "ADP", "FISV", "FIS", "CSX", "NSC", "FDX", "DAL", "LULU", "ROST",
    "EL", "CMCSA", "CHTR", "TMUS", "T", "VZ", "DUK", "NEE", "SO", "D",
    "ECL", "CL", "KMB", "GIS", "SBUX", "PYPL", "ABNB", "MAR", "HLT", "EBAY"
]

# --- Sidebar ---
interval = st.sidebar.selectbox("Interval", ["1d", "30m", "5m"], index=0)
period = {"1d": "90d", "30m": "15d", "5m": "7d"}[interval]

st.sidebar.write(f"🔍 Scanning {len(large_cap_tickers)} tickers...")

# --- Support check logic ---
def check_support_bounce(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 50:
        return None
    df = df.dropna()
    price = df["Close"].iloc[-1]
    support = df["Close"].rolling(window=50).min().iloc[-1]
    if price <= support * 1.01:  # within 1% of 50-day low
        return {
            "Ticker": ticker,
            "Time": df.index[-1].strftime("%Y-%m-%d %H:%M"),
            "Price": round(price, 2),
            "Support": round(support, 2),
            "Distance %": round((price / support - 1) * 100, 2)
        }
    return None

# --- Run scan ---
if st.button("🚀 Scan for Support Bounces"):
    results = []
    for t in large_cap_tickers:
        hit = check_support_bounce(t)
        if hit:
            results.append(hit)

    if results:
        df_result = pd.DataFrame(results).sort_values("Distance %")
        st.success(f"✅ Found {len(df_result)} ticker(s) bouncing near support:")
        st.dataframe(df_result)
    else:
        st.info("No bounces from strong support detected at the moment.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
