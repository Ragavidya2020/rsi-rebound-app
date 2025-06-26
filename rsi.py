import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Support bounce + RSI Rebound", layout="wide")
st.title("📈 Support Bounce & RSI Rebound Scanner")

st.sidebar.header("Settings")
tickers = ["NVDA","AAPL","MSFT","GOOGL","AMZN","META","TSLA",
           "JPM","BAC","KO","PG","DIS","NFLX","UNH","V","MA","WMT","CRM","ADBE","INTC"]
interval = st.sidebar.selectbox("Interval", ["1d","30m","5m"], index=0)
period_map = {"1d":"90d","30m":"15d","5m":"7d"}
period = period_map[interval]

def calculate_rsi(data, period=14):
    delta, gain = data['Close'].diff(), data['Close'].diff().clip(lower=0)
    loss = -data['Close'].diff().clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def check_bounce(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 60: return None
    df["RSI"] = calculate_rsi(df)
    df.dropna(inplace=True)
    close = df["Close"]
    rsi = df["RSI"]
    support = close.rolling(50).min().iloc[-1]
    # Last bar close near support + RSI <30 and now rising
    if abs(close.iloc[-1]-support)/support < 0.01:
        if rsi.iloc[-2] < rsi.iloc[-1] and rsi.min() < 30:
            return {"Ticker":ticker,
                    "Time":df.index[-1].strftime("%Y-%m-%d %H:%M"),
                    "Price":round(close.iloc[-1],2),
                    "RSI":round(rsi.iloc[-1],2),
                    "Support":round(support,2)}
    return None

if st.button("Run Bounce + RSI Scan"):
    res=[]
    for t in tickers:
        x=check_bounce(t)
        if x: res.append(x)
    if res:
        st.dataframe(pd.DataFrame(res))
    else:
        st.info("No ticks bouncing from support with RSI setup now.")

st.caption("Last run: "+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
