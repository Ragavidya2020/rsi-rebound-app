import streamlit as st
import yfinance as yf
import pandas as pd

st.title("RSI < 30 Rebound & EMA50 Crossover Scanner")

tickers = [
    "AAPL", "TSLA", "MSFT", "NVDA", "AMD"
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

def check_rsi_rebound_cross(df):
    df['RSI'] = calculate_rsi(df)
    df['RSI_EMA50'] = df['RSI'].ewm(span=50, adjust=False).mean()
    df = df.dropna()
    if len(df) < 3:
        return False

    # Conditions:
    rsi_3ago = df['RSI'].iloc[-3]
    rsi_2ago = df['RSI'].iloc[-2]
    rsi_1ago = df['RSI'].iloc[-1]

    ema_2ago = df['RSI_EMA50'].iloc[-2]
    ema_1ago = df['RSI_EMA50'].iloc[-1]

    # Was RSI below 30 three bars ago?
    was_oversold = rsi_3ago < 30
    # RSI was below EMA50 2 bars ago and crossed above EMA50 on last bar
    crossed_above = (rsi_2ago < ema_2ago) and (rsi_1ago > ema_1ago)

    return was_oversold and crossed_above

st.write(f"Fetching {interval} data for tickers and scanning...")

results = []

for ticker in tickers:
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 20:
        st.write(f"{ticker}: No data or too little data")
        continue

    if check_rsi_rebound_cross(df):
        latest_close = df['Close'].iloc[-1]
        latest_rsi = df['RSI'].iloc[-1]
        latest_ema = df['RSI_EMA50'].iloc[-1]
        results.append({
            "Ticker": ticker,
            "Price": round(latest_close, 2),
            "RSI": round(latest_rsi, 2),
            "RSI_EMA50": round(latest_ema, 2),
        })

if results:
    st.success(f"Tickers with RSI <30 rebound crossing EMA50:")
    st.dataframe(pd.DataFrame(results))
else:
    st.info("No tickers found matching the RSI rebound + EMA50 crossover condition at this time.")
