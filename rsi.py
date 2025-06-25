import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Rebound + EMA50 Crossover", layout="wide")
st.title("📊 RSI Rebound & EMA50 Cross Scanner")

st.sidebar.header("Scan Settings")
tickers = st.sidebar.text_area("Enter tickers (comma separated):", "AAPL,MSFT,TSLA,NVDA,GOOGL,SRPT").split(',')
tickers = [t.strip().upper() for t in tickers if t.strip()]

lookback_days = st.sidebar.number_input("Days to look back for RSI < 30", min_value=5, max_value=30, value=14)

# RSI function
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Signal detection function
def check_rsi_ema_rebound(ticker):
    df = yf.download(ticker, interval="1d", period="90d", progress=False)
    if df.empty or len(df) < lookback_days + 2:
        return None

    df['RSI'] = calculate_rsi(df)
    df['RSI_EMA50'] = df['RSI'].ewm(span=50, adjust=False).mean()
    df = df.dropna()

    recent = df.iloc[-lookback_days:]
    below_30 = recent[recent['RSI'] < 30]

    if not below_30.empty:
        # Check for RSI crossing EMA50 from below in last 2 bars
        rsi_prev = df['RSI'].iloc[-2]
        rsi_now = df['RSI'].iloc[-1]
        ema_prev = df['RSI_EMA50'].iloc[-2]
        ema_now = df['RSI_EMA50'].iloc[-1]

        if rsi_prev < ema_prev and rsi_now > ema_now:
            latest = df.iloc[-1]
            return {
                "Ticker": ticker,
                "Date": latest.name.date(),
                "Price": round(latest['Close'], 2),
                "RSI": round(rsi_now, 2),
                "RSI_EMA50": round(ema_now, 2)
            }
    return None

if st.button("📈 Run Scanner"):
    results = []
    for ticker in tickers:
        signal = check_rsi_ema_rebound(ticker)
        if signal:
            results.append(signal)

    if results:
        df_out = pd.DataFrame(results)
        st.success(f"✅ Found {len(df_out)} ticker(s) with RSI rebound crossing EMA50:")
        st.dataframe(df_out)
    else:
        st.info("No RSI rebound + EMA50 cross signals found today.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
