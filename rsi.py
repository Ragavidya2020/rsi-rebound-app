import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Simple RSI < 30 Rebound Scanner")

tickers = [
    "AAPL", "TSLA", "MSFT", "NVDA", "AMD"
]

interval = st.selectbox("Select interval", ["1d", "5m", "1m"], index=0)
period = "180d" if interval == "1d" else "30d"

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

results = []

for ticker in tickers:
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty:
        continue

    df['RSI'] = calculate_rsi(df)
    df = df.dropna()

    # Check if RSI ever went below 30 and now is above previous RSI (rebound)
    if any(df['RSI'] < 30):
        last = df.iloc[-1]
        prev = df.iloc[-2]
        if last['RSI'] > prev['RSI']:
            results.append({
                "Ticker": ticker,
                "Price": round(last['Close'], 2),
                "RSI": round(last['RSI'], 2)
            })

st.write("Tickers with RSI < 30 and RSI rising now:")
if results:
    st.dataframe(pd.DataFrame(results))
else:
    st.write("No tickers found with RSI < 30 rebound.")
