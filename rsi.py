import streamlit as st
import yfinance as yf
import pandas as pd

st.title("RSI < 30 Rebound Scanner")

tickers = [
    "AAPL", "TSLA", "MSFT", "NVDA", "AMD", "SRPT"
]

interval = st.selectbox("Select interval", options=["1d", "30m", "5m"], index=0)
period = "180d" if interval == "1d" else "60d"

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def check_rsi_rebound(df):
    df['RSI'] = calculate_rsi(df)
    df = df.dropna()
    if len(df) < 3:
        return False

    # Look at last 3 RSI values
    rsi_3ago = df['RSI'].iloc[-3]
    rsi_2ago = df['RSI'].iloc[-2]
    rsi_1ago = df['RSI'].iloc[-1]

    # Condition: RSI was below 30, and now rising (rsi_3ago <30 and rsi_1ago > rsi_2ago)
    was_oversold = rsi_3ago < 30
    is_rising = rsi_1ago > rsi_2ago

    return was_oversold and is_rising

results = []

st.write(f"Scanning {interval} data for RSI rebound...")

for ticker in tickers:
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 20:
        st.write(f"{ticker}: No data or too little data")
        continue

    if check_rsi_rebound(df):
        latest_close = df['Close'].iloc[-1]
        latest_rsi = df['RSI'].iloc[-1]
        results.append({
            "Ticker": ticker,
            "Price": round(latest_close, 2),
            "RSI": round(latest_rsi, 2),
        })

if results:
    st.success(f"Tickers with RSI < 30 and starting to rebound:")
    st.dataframe(pd.DataFrame(results))
else:
    st.info("No tickers found currently with RSI < 30 rebound.")
