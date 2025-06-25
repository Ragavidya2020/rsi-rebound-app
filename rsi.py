import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Cross Above 30 Scanner", layout="wide")
st.title("📈 RSI Scanner: RSI < 30 then crossed above 30 (anytime today)")

# Sidebar inputs
st.sidebar.header("Settings")
tickers = st.sidebar.text_area("Enter tickers (comma separated):", "AAPL,MSFT,TSLA,NVDA,GOOGL,SRPT").split(',')
tickers = [t.strip().upper() for t in tickers if t.strip()]
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "30m"], index=1)

# Period based on interval
period_map = {
    "1m": "1d",
    "5m": "5d",
    "30m": "15d"
}
period = period_map[interval]

# RSI calculation function
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_rsi_cross_above_30(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 20:
        return None

    df['RSI'] = calculate_rsi(df)
    df.dropna(inplace=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_df = df[df.index.strftime("%Y-%m-%d") == today_str]

    if today_df.empty or len(today_df) < 3:
        return None

    rsi = today_df['RSI']

    went_below_30 = (rsi < 30).any()
    crossed_above_30 = (rsi > 30).any()

    if went_below_30 and crossed_above_30:
        latest = today_df.iloc[-1]
        return {
            "Ticker": ticker,
            "Time": latest.name.strftime("%Y-%m-%d %H:%M"),
            "Price": round(latest['Close'], 2),
            "RSI": round(latest['RSI'], 2)
        }
    return None

if st.button("🚀 Run Scanner"):
    results = []
    for ticker in tickers:
        res = check_rsi_cross_above_30(ticker)
        if res:
            results.append(res)

    if results:
        df_out = pd.DataFrame(results)
        st.success(f"✅ Found {len(df_out)} tickers where RSI crossed above 30 today after being below:")
        st.dataframe(df_out)
    else:
        st.info("No tickers found matching criteria.")

st.caption("Last run: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
