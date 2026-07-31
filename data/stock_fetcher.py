"""
data/stock_fetcher.py
Downloads OHLCV price data from Yahoo Finance using yfinance.
"""

import streamlit as st
import yfinance as yf
import pandas as pd

PERIOD_MAP: dict[str, str] = {
    "1 Bulan": "1mo",
    "3 Bulan": "3mo",
    "6 Bulan": "6mo",
    "1 Tahun": "1y",
}


@st.cache_data(ttl=900)
def fetch_stock_data(ticker: str, period_label: str) -> pd.DataFrame | None:
    """
    Download OHLCV data for the given ticker and period.

    Args:
        ticker: Yahoo Finance ticker symbol, e.g. '1155.KL'
        period_label: Human-readable period, e.g. '3 Bulan'

    Returns:
        DataFrame with columns Open/High/Low/Close/Volume, indexed by date.
        Returns None if download fails or returns empty data.
    """
    period = PERIOD_MAP.get(period_label, "3mo")
    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if df.empty:
            return None
        # Flatten MultiIndex columns produced by yfinance when auto_adjust=True
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception as e:
        st.error(f"Gagal mendapatkan data untuk {ticker}: {e}")
        return None
