"""
app.py — Main entry point for the Streamlit Stock Charting app.

Run locally:
    streamlit run app.py
"""

import streamlit as st

from data.sheet_loader import load_stock_list
from data.stock_fetcher import fetch_stock_data
from logic.indicators import calculate_indicators
from ui.sidebar import render_sidebar
from ui.chart import build_chart

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal custom CSS (Muji-inspired: clean, white, spacious) ─────────────────
st.markdown(
    """
    <style>
    /* Remove default Streamlit top padding */
    .block-container { padding-top: 1.5rem; }
    /* Subtle dividers */
    hr { border-color: #F5F5F5; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Data layer ─────────────────────────────────────────────────────────────────
df_stocks = load_stock_list()

# ── UI layer — sidebar ─────────────────────────────────────────────────────────
selections = render_sidebar(df_stocks)

ticker: str = selections["ticker"]
stock_name: str = selections["stock_name"]
period: str = selections["period"]
show_sma: bool = selections["show_sma"]
show_rsi: bool = selections["show_rsi"]
show_macd: bool = selections["show_macd"]

# ── Main area ──────────────────────────────────────────────────────────────────
if not ticker:
    st.info("Sila tambah data saham ke Google Sheet anda dan semak semula sambungan.")
    st.stop()

# Fetch price data
df_ohlcv = fetch_stock_data(ticker, period)

if df_ohlcv is None:
    st.warning(
        f"Tiada data harga untuk **{stock_name}** (`{ticker}`).\n\n"
        "Sila semak kod ticker di Google Sheet (pastikan ada `.KL` untuk saham Bursa Malaysia)."
    )
    st.stop()

# Calculate indicators
df_with_indicators = calculate_indicators(
    df_ohlcv,
    show_sma=show_sma,
    show_rsi=show_rsi,
    show_macd=show_macd,
)

# Build and render chart
fig = build_chart(
    df=df_with_indicators,
    stock_name=stock_name,
    ticker=ticker,
    show_sma=show_sma,
    show_rsi=show_rsi,
    show_macd=show_macd,
)

st.plotly_chart(fig, use_container_width=True)

# ── Footer metrics ─────────────────────────────────────────────────────────────
latest = df_ohlcv.iloc[-1]
prev = df_ohlcv.iloc[-2] if len(df_ohlcv) > 1 else latest
change = latest["Close"] - prev["Close"]
change_pct = (change / prev["Close"]) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Harga Tutup", f"{latest['Close']:.3f}", f"{change:+.3f} ({change_pct:+.2f}%)")
col2.metric("Harga Buka", f"{latest['Open']:.3f}")
col3.metric("Tinggi", f"{latest['High']:.3f}")
col4.metric("Rendah", f"{latest['Low']:.3f}")
