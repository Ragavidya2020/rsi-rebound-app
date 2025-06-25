import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Intraday Rebound Scanner", layout="wide")
st.title("📈 RSI Rebound (RSI < 30 Anytime Today AND Now Rising)")

# Sidebar Inputs
st.sidebar.header("Settings")
tickers = st.sidebar.text_area("Enter tickers (comma separated):", "AAPL,MSFT,TSLA,NVDA,GOOGL,SRPT").split(',')
tickers = [t.strip().upper() for t in tickers if t.strip()]
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "30m"], index=1)

# Set period based on interval
period_map = {
    "1m": "1d",
    "5m": "5d",
    "30m": "15d"
}
period = period_map[interval]

# RSI Calculation
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Rebound Signal Logic
def check_rsi_rebound(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 15:
        return None

    df['RSI'] = calculate_rsi(df)
    df = df.dropna()

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_df = df[df.index.strftime("%Y-%m-%d") == today_str]

    if today_df.empty or len(today_df) < 3:
        return None

    rsi_values = today_df['RSI']

    if (rsi_values < 30).any() and rsi_values.iloc[-1] > rsi_values.iloc[-2]:
        latest = today_df.iloc[-1]
        return {
            "Ticker": ticker,
            "Time": latest.name.strftime("%Y-%m-%d %H:%M"),
            "Price": round(latest['Close'], 2),
            "RSI": round(latest['RSI'], 2)
        }

    return None

# Scanner Execution
if st.button("🚀 Run RSI Scanner"):
    signals = []
    for ticker in tickers:
        result = check_rsi_rebound(ticker)
        if result:
            signals.append(result)

    if signals:
        df_signals = pd.DataFrame(signals)
        st.success(f"✅ Found {len(df_signals)} RSI rebound(s):")
        st.dataframe(df_signals)
    else:
        st.info("No RSI rebound signals found today.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
