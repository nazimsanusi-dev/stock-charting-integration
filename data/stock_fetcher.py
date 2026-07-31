"""
data/stock_fetcher.py
Downloads OHLCV price data from Yahoo Finance using yfinance.
Supports daily / weekly / monthly intervals and up to 10-year history.
"""

import streamlit as st
import yfinance as yf
import pandas as pd

PERIOD_MAP: dict[str, str] = {
    "3 Bulan":  "3mo",
    "6 Bulan":  "6mo",
    "1 Tahun":  "1y",
    "2 Tahun":  "2y",
    "5 Tahun":  "5y",
    "10 Tahun": "10y",
}

INTERVAL_MAP: dict[str, str] = {
    "Harian":   "1d",
    "Mingguan": "1wk",
    "Bulanan":  "1mo",
}


@st.cache_data(ttl=900)
def fetch_stock_data(
    ticker: str,
    period_label: str,
    interval_label: str = "Harian",
) -> pd.DataFrame | None:
    """
    Download OHLCV data for the given ticker, period and interval.

    Args:
        ticker:         Yahoo Finance ticker symbol, e.g. '1155.KL'
        period_label:   Human-readable period, e.g. '1 Tahun'
        interval_label: 'Harian' | 'Mingguan' | 'Bulanan'

    Returns:
        DataFrame with columns Open/High/Low/Close/Volume, indexed by datetime.
        Returns None if download fails or returns empty data.
    """
    period   = PERIOD_MAP.get(period_label, "1y")
    interval = INTERVAL_MAP.get(interval_label, "1d")
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,
        )
        if df.empty:
            return None
        # Flatten MultiIndex columns produced by yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        # Remove timezone info to keep index naive (consistent)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception as e:
        st.error(f"Gagal mendapatkan data untuk {ticker}: {e}")
        return None
