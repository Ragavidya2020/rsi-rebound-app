import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Support Bounce Scanner", layout="wide")
st.title("🔵 Support Bounce Scanner (Price Near 50‑day Low)")

# ---- Settings ----
tickers = [
    "NVDA","AAPL","MSFT","GOOGL","AMZN","META","TSLA",
    "JPM","BAC","KO","PG","DIS","NFLX","UNH","V",
    "MA","WMT","CRM","ADBE","INTC"
]
interval = st.sidebar.selectbox("Interval", ["1d", "30m", "5m"], index=0)
period = "90d" if interval=="1d" else ("15d" if interval=="30m" else "7d")

st.sidebar.write("Scanning 20 large-cap names for bounce from 50‑day low...")

def check_support_bounce(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 50:
        return None
    close = df["Close"]
    support = close.rolling(50).min().iloc[-1]
    price = close.iloc[-1]
    if price <= support * 1.01:  # within 1% of 50‑day low
        return {
            "Ticker": ticker,
            "Time": df.index[-1].strftime("%Y-%m-%d %H:%M"),
            "Price": round(price, 2),
            "Support": round(support, 2),
            "Dist %": round((price/support - 1)*100, 2)
        }
    return None

if st.button("🔍 Scan Support Bounce"):
    hits = [check_support_bounce(t) for t in tickers]
    hits = [h for h in hits if h]
    if hits:
        df_hits = pd.DataFrame(hits).sort_values("Dist %")
        st.success(f"Found {len(df_hits)} stocks near support:")
        st.dataframe(df_hits)
    else:
        st.info("No large-cap tickers are within 1% of 50‑day low right now.")

st.caption("Last scan: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
