"""
ui/sidebar.py
Renders the main sidebar controls and returns all user selections.
The sheet selector is handled separately in app.py (phase-1 sidebar).
"""

import streamlit as st
import pandas as pd

EMA_OPTIONS:      list[int] = [5, 10, 20, 50, 100, 150, 200]
PERIOD_OPTIONS:   list[str] = ["3 Bulan", "6 Bulan", "1 Tahun", "2 Tahun", "5 Tahun", "10 Tahun"]
TIMEFRAME_OPTIONS: list[str] = ["Harian", "Mingguan", "Bulanan"]


def render_sidebar(df_stocks: pd.DataFrame) -> dict:
    """
    Render sidebar controls and return all user selections.

    Args:
        df_stocks: DataFrame with columns Name and Symbol.

    Returns:
        dict with all user selections.
    """
    with st.sidebar:
        # ── View mode (Tunggal / Grid) ────────────────────────────────────────
        st.markdown("**👁️ Mod Paparan**")
        view_mode: str = st.radio(
            "view_mode",
            ["Tunggal", "Grid"],
            horizontal=True,
            label_visibility="collapsed",
            key="view_mode",
        )

        # Number of columns — only relevant in Grid mode
        n_cols: int = 3
        if view_mode == "Grid":
            n_cols = st.radio(
                "Bilangan lajur",
                [2, 3, 4],
                index=1,
                horizontal=True,
                key="n_cols",
            )

        st.markdown("---")

        # ── Stock listing ─────────────────────────────────────────────────────
        st.markdown("**📊 Senarai Saham**")

        selected_stocks: list[dict] = []
        ticker: str = ""
        stock_name: str = ""

        if df_stocks.empty:
            st.warning("Tiada saham dimuatkan dari Sheet.")
        else:
            search: str = st.text_input(
                "Cari",
                placeholder="🔍  Nama atau kod ticker…",
                key="stock_search",
                label_visibility="collapsed",
            )

            mask = pd.Series([True] * len(df_stocks), index=df_stocks.index)
            if search.strip():
                q = search.strip().lower()
                mask = (
                    df_stocks["Name"].str.lower().str.contains(q, na=False)
                    | df_stocks["Symbol"].str.lower().str.contains(q, na=False)
                )

            filtered = df_stocks[mask].reset_index(drop=True)

            if filtered.empty:
                st.caption("Tiada hasil carian.")
            elif view_mode == "Grid":
                # Grid: show count badge; all filtered stocks are used automatically
                st.caption(f"{len(filtered)} saham akan dipaparkan")
                selected_stocks = [
                    {"name": row["Name"], "ticker": row["Symbol"]}
                    for _, row in filtered.iterrows()
                ]
            else:
                # Tunggal: scrollable radio to pick one stock
                options = [
                    f"{row['Name']} [{row['Symbol']}]"
                    for _, row in filtered.iterrows()
                ]
                with st.container(height=290, border=False):
                    chosen_label: str | None = st.radio(
                        "Pilih saham",
                        options=options,
                        label_visibility="collapsed",
                        key="single_stock",
                    )
                if chosen_label:
                    sym = chosen_label.rsplit("[", 1)[-1].rstrip("]")
                    nm  = chosen_label.rsplit(" [", 1)[0]
                    selected_stocks = [{"name": nm, "ticker": sym}]
                    ticker     = sym
                    stock_name = nm

        st.markdown("---")

        # ── Timeframe ─────────────────────────────────────────────────────────
        st.markdown("**⏱️ Timeframe**")
        timeframe: str = st.radio(
            "timeframe",
            TIMEFRAME_OPTIONS,
            horizontal=True,
            label_visibility="collapsed",
            key="timeframe",
        )

        # ── Gabung Timeframe — independent toggle ─────────────────────────────
        gabung_timeframe: bool = st.toggle(
            "⟂ Gabung Timeframe",
            value=False,
            key="gabung_timeframe",
        )
        timeframe2: str | None = None
        if gabung_timeframe:
            other_tf = [t for t in TIMEFRAME_OPTIONS if t != timeframe]
            timeframe2 = st.radio(
                "+ Timeframe 2",
                other_tf,
                horizontal=True,
                key="timeframe2",
            )

        # ── Period ────────────────────────────────────────────────────────────
        st.markdown("**📅 Tempoh Data**")
        period: str = st.select_slider(
            "period",
            options=PERIOD_OPTIONS,
            value="1 Tahun",
            label_visibility="collapsed",
            key="period",
        )

        st.markdown("---")

        # ── Indicators ────────────────────────────────────────────────────────
        st.markdown("**📈 Indikator**")

        with st.expander("EMA", expanded=False):
            ema_periods: list[int] = st.multiselect(
                "Tempoh EMA",
                EMA_OPTIONS,
                default=[20, 50],
                label_visibility="collapsed",
                key="ema_periods",
            )

        col_a, col_b = st.columns(2)
        show_rsi  = col_a.checkbox("RSI (14)",  value=True,  key="show_rsi")
        show_cvd  = col_b.checkbox("CVD",       value=False, key="show_cvd")
        show_cmf  = col_a.checkbox("CMF (20)",  value=False, key="show_cmf")
        show_macd = col_b.checkbox("MACD",      value=True,  key="show_macd")

        macd_fast, macd_slow, macd_signal = 12, 26, 9
        if show_macd:
            with st.expander("MACD Tetapan", expanded=False):
                macd_fast   = st.number_input("Fast",   2,  50, 12, key="macd_fast")
                macd_slow   = st.number_input("Slow",   5, 200, 26, key="macd_slow")
                macd_signal = st.number_input("Signal", 1,  50,  9, key="macd_signal")

        st.markdown("---")
        st.caption("Data: Yahoo Finance · Senarai: Google Sheets")

    return {
        "view_mode":        view_mode,
        "n_cols":           int(n_cols),
        "gabung_timeframe": gabung_timeframe,
        "selected_stocks":  selected_stocks,
        "ticker":           ticker,
        "stock_name":       stock_name,
        "timeframe":        timeframe,
        "timeframe2":       timeframe2,
        "period":           period,
        "ema_periods":      ema_periods,
        "show_rsi":         show_rsi,
        "show_macd":        show_macd,
        "show_cvd":         show_cvd,
        "show_cmf":         show_cmf,
        "macd_fast":        int(macd_fast),
        "macd_slow":        int(macd_slow),
        "macd_signal":      int(macd_signal),
    }
