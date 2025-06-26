import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Support Bounce Scanner", layout="wide")
st.title("🔵 Support Bounce Scanner (Price Near 50‑period Low)")

# ---- Settings ----
tickers = [
    "NVDA","AAPL","MSFT","GOOGL","AMZN","META","TSLA",
    "JPM","BAC","KO","PG","DIS","NFLX","UNH","V",
    "MA","WMT","CRM","ADBE","INTC"
]
interval = st.sidebar.selectbox("Interval", ["1d", "30m", "5m"], index=0)
period = "90d" if interval=="1d" else ("15d" if interval=="30m" else "7d")

st.sidebar.write("Scanning 20 large-cap stocks for bounce from support...")

def check_support_bounce(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 50:
        return None

    df = df.dropna()
    close_prices = df["Close"]
    latest_price = close_prices.iloc[-1]
    support_level = close_prices.rolling(50).min().iloc[-1]

    # Ensure both are floats (not Series)
    if float(latest_price) <= float(support_level) * 1.01:
        return {
            "Ticker": ticker,
            "Time": df.index[-1].strftime("%Y-%m-%d %H:%M"),
            "Price": round(float(latest_price), 2),
            "Support": round(float(support_level), 2),
            "Dist %": round((float(latest_price)/float(support_level) - 1) * 100, 2)
        }
    return None

if st.button("🔍 Scan Support Bounce"):
    results = []
    for t in tickers:
        signal = check_support_bounce(t)
        if signal:
            results.append(signal)

    if results:
        df_out = pd.DataFrame(results).sort_values("Dist %")
        st.success(f"✅ Found {len(df_out)} stock(s) near support zone:")
        st.dataframe(df_out)
    else:
        st.info("No support zone bounces found at this time.")

st.caption("Last scan: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
