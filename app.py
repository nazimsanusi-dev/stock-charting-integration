"""
app.py — Main entry point for the Streamlit Stock Charting app.

Run locally:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

from data.sheet_loader import load_sheet_names, load_stock_list
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

# ── Global CSS (Muji-inspired) ─────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .block-container          { padding-top: 1.2rem; padding-bottom: 0.5rem; }
    hr                        { border-color: #F5F5F5; }
    [data-testid="stSidebar"] { background: #FAFAFA; }
    /* Keep metric delta colours */
    [data-testid="stMetricDelta"] > div { font-size: 0.78rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _indicator_config(params: dict) -> dict:
    """Extract indicator-related keys from the full params dict."""
    return {
        "ema_periods": params.get("ema_periods", []),
        "show_rsi":    params.get("show_rsi",    False),
        "show_macd":   params.get("show_macd",   False),
        "show_cvd":    params.get("show_cvd",    False),
        "show_cmf":    params.get("show_cmf",    False),
        "macd_fast":   params.get("macd_fast",   12),
        "macd_slow":   params.get("macd_slow",   26),
        "macd_signal": params.get("macd_signal",  9),
    }


def render_stock_panel(
    ticker: str,
    name: str,
    period: str,
    timeframe: str,
    ind_cfg: dict,
    height: int = 700,
    show_metrics: bool = True,
) -> None:
    """Fetch → calculate → chart → metrics for one stock."""
    df = fetch_stock_data(ticker, period, timeframe)
    if df is None or df.empty:
        st.warning(
            f"Tiada data untuk **{name}** (`{ticker}`).  "
            "Semak kod ticker (contoh: `1155.KL` untuk Bursa Malaysia)."
        )
        return

    df_ind = calculate_indicators(df, ind_cfg)
    title  = f"{name}  ·  {ticker}  ·  {timeframe}  ·  {period}"
    fig    = build_chart(df_ind, title, ind_cfg, timeframe=timeframe, height=height)
    # unique key prevents Streamlit duplicate-key warnings in grid/combined views
    st.plotly_chart(fig, use_container_width=True,
                    key=f"chart__{ticker}__{timeframe}__{period}__{height}")

    if show_metrics and len(df) >= 1:
        latest = df.iloc[-1]
        prev   = df.iloc[-2] if len(df) > 1 else latest
        chg    = float(latest["Close"]) - float(prev["Close"])
        chg_p  = (chg / float(prev["Close"])) * 100 if float(prev["Close"]) != 0 else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tutup", f"{float(latest['Close']):.3f}", f"{chg_p:+.2f}%")
        c2.metric("Buka",  f"{float(latest['Open']):.3f}")
        c3.metric("Tinggi",f"{float(latest['High']):.3f}")
        c4.metric("Rendah",f"{float(latest['Low']):.3f}")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — phase 1: sheet selector
# ══════════════════════════════════════════════════════════════════════════════
sheet_names: list[str] = load_sheet_names()

with st.sidebar:
    st.markdown("## 📈 Stock Monitor")
    selected_sheet: str = st.selectbox(
        "📋 Sheet",
        sheet_names,
        key="selected_sheet",
    )
    st.markdown("---")

# ── Load stock list for the selected sheet ─────────────────────────────────────
df_stocks: pd.DataFrame = load_stock_list(selected_sheet)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — phase 2: all other controls
# ══════════════════════════════════════════════════════════════════════════════
params: dict = render_sidebar(df_stocks)

# Derived values
view_mode:  str       = params["view_mode"]
period:     str       = params["period"]
timeframe:  str       = params["timeframe"]
timeframe2: str | None = params.get("timeframe2")
ind_cfg:    dict      = _indicator_config(params)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

# ── TUNGGAL ───────────────────────────────────────────────────────────────────
if view_mode == "Tunggal":
    stocks = params.get("selected_stocks", [])
    if not stocks:
        st.info("👈  Pilih saham dari senarai di sebelah kiri.")
        st.stop()

    stock = stocks[0]
    render_stock_panel(
        stock["ticker"], stock["name"],
        period, timeframe, ind_cfg, height=700,
    )


# ── GRID 3×3 ──────────────────────────────────────────────────────────────────
elif view_mode == "Grid 3×3":
    stocks = params.get("selected_stocks", [])
    if not stocks:
        st.info("👈  Pilih sehingga 9 saham dari senarai di sebelah kiri.")
        st.stop()

    st.markdown(f"#### Grid Saham  ·  {timeframe}  ·  {period}")
    st.markdown("---")

    for row_start in range(0, len(stocks), 3):
        row_stocks = stocks[row_start : row_start + 3]
        cols = st.columns(len(row_stocks), gap="small")
        for col, stock in zip(cols, row_stocks):
            with col:
                st.markdown(f"**{stock['name']}**  `{stock['ticker']}`")
                render_stock_panel(
                    stock["ticker"], stock["name"],
                    period, timeframe, ind_cfg,
                    height=430,
                    show_metrics=True,
                )
        st.markdown("---")


# ── GABUNG TIMEFRAME ──────────────────────────────────────────────────────────
elif view_mode == "Gabung Timeframe":
    stocks = params.get("selected_stocks", [])
    if not stocks:
        st.info("👈  Pilih saham dari senarai di sebelah kiri.")
        st.stop()

    stock = stocks[0]
    tf2   = timeframe2 or (
        "Mingguan" if timeframe == "Harian" else "Harian"
    )

    st.markdown(
        f"#### {stock['name']}  ·  `{stock['ticker']}`  ·  "
        f"**{timeframe}** + **{tf2}**  ·  {period}"
    )
    st.markdown("---")

    col_l, col_r = st.columns(2, gap="medium")
    with col_l:
        st.markdown(f"##### ⏱ {timeframe}")
        render_stock_panel(
            stock["ticker"], stock["name"],
            period, timeframe, ind_cfg, height=560,
        )
    with col_r:
        st.markdown(f"##### ⏱ {tf2}")
        render_stock_panel(
            stock["ticker"], stock["name"],
            period, tf2, ind_cfg, height=560,
        )
