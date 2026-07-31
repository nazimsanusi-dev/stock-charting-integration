"""
ui/sidebar.py
Renders the main sidebar controls and returns all user selections.
The sheet selector is handled separately in app.py (phase-1 sidebar),
so this function receives an already-loaded stock DataFrame.
"""

import streamlit as st
import pandas as pd

EMA_OPTIONS:     list[int] = [5, 10, 20, 50, 100, 150, 200]
PERIOD_OPTIONS:  list[str] = ["3 Bulan", "6 Bulan", "1 Tahun", "2 Tahun", "5 Tahun", "10 Tahun"]
TIMEFRAME_OPTIONS: list[str] = ["Harian", "Mingguan", "Bulanan"]


def render_sidebar(df_stocks: pd.DataFrame) -> dict:
    """
    Render sidebar controls (view mode, stock list, timeframe, period,
    indicators).  Sheet selector is handled by app.py before calling this.

    Args:
        df_stocks: DataFrame with columns Name and Symbol.

    Returns:
        dict with all user selections.
    """
    with st.sidebar:
        # ── View mode ────────────────────────────────────────────────────────
        st.markdown("**👁️ Mod Paparan**")
        view_mode: str = st.radio(
            "view_mode",
            ["Tunggal", "Grid 3×3", "Gabung Timeframe"],
            horizontal=True,
            label_visibility="collapsed",
            key="view_mode",
        )

        st.markdown("---")

        # ── Stock listing ────────────────────────────────────────────────────
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
            # Format: "Name [SYMBOL]" — square brackets so we can split safely
            options = [
                f"{row['Name']} [{row['Symbol']}]"
                for _, row in filtered.iterrows()
            ]

            if not options:
                st.caption("Tiada hasil carian.")
            elif view_mode == "Grid 3×3":
                chosen_labels: list[str] = st.multiselect(
                    "Pilih sehingga 9 saham",
                    options=options,
                    max_selections=9,
                    label_visibility="collapsed",
                    key="grid_stocks",
                )
                for lbl in chosen_labels:
                    sym = lbl.rsplit("[", 1)[-1].rstrip("]")
                    nm  = lbl.rsplit(" [", 1)[0]
                    selected_stocks.append({"name": nm, "ticker": sym})
                if selected_stocks:
                    ticker     = selected_stocks[0]["ticker"]
                    stock_name = selected_stocks[0]["name"]
            else:
                # Scrollable radio list via st.container(height=…)
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

        # ── Timeframe ────────────────────────────────────────────────────────
        st.markdown("**⏱️ Timeframe**")
        timeframe: str = st.radio(
            "timeframe",
            TIMEFRAME_OPTIONS,
            horizontal=True,
            label_visibility="collapsed",
            key="timeframe",
        )

        timeframe2: str | None = None
        if view_mode == "Gabung Timeframe":
            other_tf = [t for t in TIMEFRAME_OPTIONS if t != timeframe]
            timeframe2 = st.radio(
                "+ Timeframe 2",
                other_tf,
                horizontal=True,
                key="timeframe2",
            )

        # ── Period ───────────────────────────────────────────────────────────
        st.markdown("**📅 Tempoh Data**")
        period: str = st.select_slider(
            "period",
            options=PERIOD_OPTIONS,
            value="1 Tahun",
            label_visibility="collapsed",
            key="period",
        )

        st.markdown("---")

        # ── Indicators ───────────────────────────────────────────────────────
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
        "view_mode":      view_mode,
        "selected_stocks": selected_stocks,
        "ticker":         ticker,
        "stock_name":     stock_name,
        "timeframe":      timeframe,
        "timeframe2":     timeframe2,
        "period":         period,
        "ema_periods":    ema_periods,
        "show_rsi":       show_rsi,
        "show_macd":      show_macd,
        "show_cvd":       show_cvd,
        "show_cmf":       show_cmf,
        "macd_fast":      int(macd_fast),
        "macd_slow":      int(macd_slow),
        "macd_signal":    int(macd_signal),
    }
