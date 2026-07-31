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

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Push content below Streamlit's fixed top toolbar */
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0.5rem; }
    hr               { border-color: #F5F5F5; }

    /* Compact OHLC metrics row */
    .ohlc-bar {
        font-size: 0.76rem;
        color: #757575;
        margin: 2px 0 8px 0;
        line-height: 1.6;
    }
    .ohlc-bar b   { color: #424242; }
    .ohlc-bar .up { color: #26A69A; font-weight: 600; }
    .ohlc-bar .dn { color: #EF5350; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _indicator_config(params: dict) -> dict:
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


def _ohlc_bar(df: pd.DataFrame) -> None:
    """Render a compact single-line OHLC summary below the chart."""
    if len(df) < 1:
        return
    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) > 1 else latest
    chg    = float(latest["Close"]) - float(prev["Close"])
    chg_p  = (chg / float(prev["Close"])) * 100 if float(prev["Close"]) != 0 else 0.0
    cls    = "up" if chg_p >= 0 else "dn"
    sign   = "▲" if chg_p >= 0 else "▼"
    st.markdown(
        f"<div class='ohlc-bar'>"
        f"<b>T</b> {float(latest['Close']):.3f} "
        f"<span class='{cls}'>{sign} {abs(chg_p):.2f}%</span>"
        f"&ensp;·&ensp;<b>B</b> {float(latest['Open']):.3f}"
        f"&ensp;·&ensp;<b>H</b> {float(latest['High']):.3f}"
        f"&ensp;·&ensp;<b>R</b> {float(latest['Low']):.3f}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_stock_panel(
    ticker: str,
    name: str,
    period: str,
    timeframe: str,
    ind_cfg: dict,
    height: int = 700,
) -> None:
    """Fetch → calculate → chart → compact OHLC bar for one stock/timeframe."""
    df = fetch_stock_data(ticker, period, timeframe)
    if df is None or df.empty:
        st.warning(
            f"Tiada data untuk **{name}** (`{ticker}`).  "
            "Semak kod ticker."
        )
        return

    df_ind = calculate_indicators(df, ind_cfg)
    title  = f"{name}  ·  {ticker}  ·  {timeframe}  ·  {period}"
    fig    = build_chart(df_ind, title, ind_cfg, timeframe=timeframe, height=height)
    st.plotly_chart(fig, width="stretch",
                    key=f"chart__{ticker}__{timeframe}__{period}__{height}")
    _ohlc_bar(df)


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

# ── Load stock list for selected sheet ────────────────────────────────────────
df_stocks: pd.DataFrame = load_stock_list(selected_sheet)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — phase 2: all other controls
# ══════════════════════════════════════════════════════════════════════════════
params: dict = render_sidebar(df_stocks)

# Derived values
view_mode:        str        = params["view_mode"]
n_cols:           int        = params["n_cols"]
gabung_timeframe: bool       = params["gabung_timeframe"]
period:           str        = params["period"]
timeframe:        str        = params["timeframe"]
timeframe2:       str | None = params.get("timeframe2")
ind_cfg:          dict       = _indicator_config(params)

# Ensure timeframe2 always has a value when gabung is active
if gabung_timeframe and not timeframe2:
    timeframe2 = next(
        t for t in ["Harian", "Mingguan", "Bulanan"] if t != timeframe
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

stocks: list[dict] = params.get("selected_stocks", [])

# ── TUNGGAL ───────────────────────────────────────────────────────────────────
if view_mode == "Tunggal":
    if not stocks:
        st.info("👈  Pilih saham dari senarai di sebelah kiri.")
        st.stop()

    stock = stocks[0]

    if gabung_timeframe:
        st.markdown(
            f"#### {stock['name']}  ·  `{stock['ticker']}`  ·  "
            f"**{timeframe}** + **{timeframe2}**"
        )
        st.markdown("---")
        col_l, col_r = st.columns(2, gap="medium")
        with col_l:
            st.markdown(f"##### ⏱ {timeframe}")
            render_stock_panel(stock["ticker"], stock["name"],
                               period, timeframe, ind_cfg, height=580)
        with col_r:
            st.markdown(f"##### ⏱ {timeframe2}")
            render_stock_panel(stock["ticker"], stock["name"],
                               period, timeframe2, ind_cfg, height=580)
    else:
        render_stock_panel(stock["ticker"], stock["name"],
                           period, timeframe, ind_cfg, height=700)


# ── GRID ──────────────────────────────────────────────────────────────────────
elif view_mode == "Grid":
    if not stocks:
        st.info("👈  Tiada saham. Semak sambungan Google Sheet atau tapis carian.")
        st.stop()

    label_tf = (f"**{timeframe}** + **{timeframe2}**"
                if gabung_timeframe else f"**{timeframe}**")
    st.markdown(
        f"#### Grid Saham  ·  {label_tf}  ·  {period}  "
        f"·  {len(stocks)} saham  ·  {n_cols} lajur"
    )
    st.markdown("---")

    # Smaller charts when two are stacked per cell
    cell_h = 290 if gabung_timeframe else 420

    for row_start in range(0, len(stocks), n_cols):
        row_stocks = stocks[row_start : row_start + n_cols]
        cols = st.columns(len(row_stocks), gap="small")

        for col, stock in zip(cols, row_stocks):
            with col:
                st.markdown(
                    f"<div style='font-size:0.82rem;font-weight:600;"
                    f"margin-bottom:3px'>{stock['name']}"
                    f"&ensp;<code style='font-weight:400;font-size:0.75rem'>"
                    f"{stock['ticker']}</code></div>",
                    unsafe_allow_html=True,
                )
                if gabung_timeframe:
                    st.markdown(
                        f"<span style='font-size:0.68rem;color:#9E9E9E'>"
                        f"⏱ {timeframe}</span>",
                        unsafe_allow_html=True,
                    )
                    render_stock_panel(stock["ticker"], stock["name"],
                                       period, timeframe, ind_cfg, height=cell_h)
                    st.markdown(
                        f"<span style='font-size:0.68rem;color:#9E9E9E'>"
                        f"⏱ {timeframe2}</span>",
                        unsafe_allow_html=True,
                    )
                    render_stock_panel(stock["ticker"], stock["name"],
                                       period, timeframe2, ind_cfg, height=cell_h)
                else:
                    render_stock_panel(stock["ticker"], stock["name"],
                                       period, timeframe, ind_cfg, height=cell_h)

        st.markdown("---")
