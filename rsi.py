import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Support Bounce Scanner", layout="wide")
st.title("📉 Support Bounce Scanner (Based on 50-period low)")

# --- Ticker groups by price category ---
price_below_50 = [
    "WBD", "CHPT", "CANO", "F", "PBR", "T", "VZ", "BAC", "SOFI", "PLUG", "OPEN", "SIRI", "MRO", "BB",
    "BBD", "PENN", "SABR", "MFA", "NOK", "GGB", "VALE", "INTC", "CLF", "MGM", "PFE", "BMY", "GM", "APA",
    "X", "AR", "RIG", "NCLH", "CCL", "UAL", "DAL", "LYV", "HST", "WOLF", "RIVN", "LUMN", "FCX", "WBA",
    "KGC", "TFC", "HBAN", "ALLY", "RF", "KEY", "C", "ET", "XOM"
]

price_below_100 = [
    "DIS", "SBUX", "CVS", "PYPL", "ABNB", "CRM", "SNAP", "GILD", "MRNA", "UBER", "LYFT", "DKNG", "LULU",
    "ROKU", "BIIB", "ATVI", "WDC", "MU", "AMD", "AAL", "WMT", "KO", "PEP", "CSCO", "VLO", "OXY", "PXD",
    "EOG", "ZIM", "SQ", "NET", "DDOG", "DOCU", "BIDU", "SHOP", "TGT", "LOW", "HD", "MDT", "GE", "MMM",
    "DE", "NUE", "CAT", "BA", "LMT", "GD", "TSM", "NXPI"
]

price_above_100 = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "V", "MA", "AVGO", "COST", "NFLX", "REGN",
    "EL", "ORLY", "ADBE", "ISRG", "NOW", "BKNG", "ANET", "ADI", "VRTX", "FICO", "ASML", "CDNS", "CRWD",
    "PANW", "MELI", "QCOM", "TXN", "CMG", "LRCX", "ZS", "CHTR", "IDXX", "MSCI", "TMO", "EQIX", "SPOT",
    "ROST", "ALGN", "SNPS", "INTU", "AZO", "BLK", "HUM", "MOH", "CI", "PGR"
]

ticker_groups = {
    "Below $50": price_below_50,
    "Below $100": price_below_100,
    "Above $100": price_above_100,
    "All Combined": list(set(price_below_50 + price_below_100 + price_above_100))
}

# --- Sidebar controls ---
interval = st.sidebar.selectbox("Chart Interval", ["1d", "30m", "5m"], index=0)
period = "90d" if interval == "1d" else ("15d" if interval == "30m" else "7d")
group_choice = st.sidebar.selectbox("Select Ticker Group", list(ticker_groups.keys()), index=3)

tickers = ticker_groups[group_choice]
st.sidebar.write(f"🔍 Scanning {len(tickers)} stocks from group: **{group_choice}**")

# --- Main scan logic ---
def check_support_bounce(ticker):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    if df.empty or len(df) < 50:
        return None

    df = df.dropna()
    close_prices = df["Close"]
    latest_price = close_prices.iloc[-1]
    support_level = close_prices.rolling(50).min().iloc[-1]

    if float(latest_price) <= float(support_level) * 1.01:
        return {
            "Ticker": ticker,
            "Time": df.index[-1].strftime("%Y-%m-%d %H:%M"),
            "Price": round(float(latest_price), 2),
            "Support": round(float(support_level), 2),
            "Dist %": round((float(latest_price)/float(support_level) - 1) * 100, 2)
        }
    return None

# --- Run scan ---
if st.button("🚀 Run Scan"):
    results = []
    for t in tickers:
        signal = check_support_bounce(t)
        if signal:
            results.append(signal)

    if results:
        df_out = pd.DataFrame(results).sort_values("Dist %")
        st.success(f"✅ Found {len(df_out)} stock(s) near 50-period support:")
        st.dataframe(df_out)
    else:
        st.info("No strong support signals found right now.")

st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
