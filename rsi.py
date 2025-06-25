import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="📈 RSI Rebound After Below 30", layout="wide")
st.title("📈 RSI Scanner: Rebound After RSI < 30 (Anytime Today)")

# Sidebar settings
st.sidebar.header("Settings")
tickers = st.sidebar.text_area("Enter tickers (comma separated):", "AAPL,MSFT,TSLA,NVDA,GOOGL,SRPT").split(',')
tickers = [t.strip().upper() for t in tickers if t.strip()]
interval = st.sidebar.selectbox("Timeframe", ["1m", "5m", "30m"], index=1)

# Period for yfinance
period_map = {
    "1m": "1d",
    "5m": "5d",
    "30m": "15d"
}
period = period_map[interval]

# RSI calculation
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Rebound detector
def check_rsi_rebound_after_30(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 20:
        return None

    df['RSI'] = calculate_rsi(df).dropna()
    df.dropna(inplace=True)

    # Get today's data only
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_df = df[df.index.strftime("%Y-%m-%d") == today_str]
    if today_df.empty or len(today_df) < 3:
        return None

    rsi_series = today_df['RSI']

    # Step 1: Was RSI < 30 at any time?
    went_below_30 = (rsi_series < 30).any()

    # Step 2: Find first time RSI crosses above 30 after being below
    crossed_above_30 = rsi_series[rsi_series > 30]

    if went_below_30 and not crossed_above_30.empty:
        last_rsi = rsi_series.iloc[-1]
        prev_rsi = rsi_series.iloc[-2]

        # Step 3: Is RSI still rising now?
        if last_rsi > prev_rsi:
            latest = today_df.iloc[-1]
            return {
                "Ticker": ticker,
                "Time": latest.name.strftime("%Y-%m-%d %H:%M"),
                "Price": round(latest['Close'], 2),
                "RSI": round(last_rsi, 2)
            }

    return None

# Run button
if st.button("🚀 Run RSI Rebound Scanner"):
    signals = []
    for ticker in tickers:
        result = check_rsi_rebound_after_30(ticker)
        if result:
            signals.append(result)

    if signals:
        df_out = pd_
