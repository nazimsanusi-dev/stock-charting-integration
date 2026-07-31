"""
ui/sidebar.py
Renders the Streamlit sidebar and returns user selections.
"""

import streamlit as st
import pandas as pd
from data.stock_fetcher import PERIOD_MAP


def render_sidebar(df_stocks: pd.DataFrame) -> dict:
    """
    Render the sidebar UI and return the user's selections.

    Args:
        df_stocks: DataFrame with columns Name and Symbol.

    Returns:
        dict with keys: stock_name, ticker, period, show_sma, show_rsi, show_macd
    """
    st.sidebar.title("📊 Stock Monitor")
    st.sidebar.markdown("---")

    # Stock selector
    st.sidebar.subheader("Pilih Saham")
    if df_stocks.empty:
        st.sidebar.warning("Tiada saham dimuatkan dari Google Sheet.")
        stock_name = ""
        ticker = ""
    else:
        stock_name = st.sidebar.selectbox(
            "Nama Syarikat",
            options=df_stocks["Name"].tolist(),
            label_visibility="collapsed",
        )
        ticker_row = df_stocks[df_stocks["Name"] == stock_name]
        ticker = ticker_row["Symbol"].values[0] if not ticker_row.empty else ""

    st.sidebar.markdown("---")

    # Period selector
    st.sidebar.subheader("Tempoh Masa")
    period = st.sidebar.radio(
        "Tempoh",
        options=list(PERIOD_MAP.keys()),
        index=1,  # default: 3 Bulan
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")

    # Indicator toggles
    st.sidebar.subheader("📈 Indikator Teknikal")
    show_sma = st.sidebar.checkbox("SMA (20 & 50)", value=True)
    show_rsi = st.sidebar.checkbox("RSI (14)", value=True)
    show_macd = st.sidebar.checkbox("MACD (12, 26, 9)", value=True)

    st.sidebar.markdown("---")
    st.sidebar.caption("Data: Yahoo Finance · Senarai: Google Sheets")

    return {
        "stock_name": stock_name,
        "ticker": ticker,
        "period": period,
        "show_sma": show_sma,
        "show_rsi": show_rsi,
        "show_macd": show_macd,
    }
