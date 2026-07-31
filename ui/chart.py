"""
ui/chart.py
Builds the interactive Plotly candlestick chart with optional indicators.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Colour palette (Muji-inspired)
COLOR_UP = "#26A69A"
COLOR_DOWN = "#EF5350"
COLOR_SMA20 = "#2196F3"
COLOR_SMA50 = "#FF9800"
COLOR_RSI = "#9C27B0"
COLOR_MACD = "#2196F3"
COLOR_SIGNAL = "#FF9800"
COLOR_HIST_POS = "#26A69A"
COLOR_HIST_NEG = "#EF5350"
COLOR_BG = "#FFFFFF"
COLOR_GRID = "#F5F5F5"


def build_chart(
    df: pd.DataFrame,
    stock_name: str,
    ticker: str,
    show_sma: bool,
    show_rsi: bool,
    show_macd: bool,
) -> go.Figure:
    """
    Build a Plotly figure with candlestick chart and optional indicator sub-charts.

    Args:
        df: DataFrame with OHLCV + indicator columns.
        stock_name: Display name of the stock.
        ticker: Ticker code shown in the title.
        show_sma: Overlay SMA lines on the candlestick.
        show_rsi: Add RSI sub-chart.
        show_macd: Add MACD sub-chart.

    Returns:
        Plotly Figure ready for st.plotly_chart().
    """
    # Determine subplot rows
    sub_charts = [c for c in [show_rsi, show_macd] if c]
    n_rows = 1 + len(sub_charts)
    row_heights = [0.6] + [0.2] * len(sub_charts)

    subplot_titles = [f"{stock_name} ({ticker})"]
    if show_rsi:
        subplot_titles.append("RSI (14)")
    if show_macd:
        subplot_titles.append("MACD (12, 26, 9)")

    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=row_heights,
        subplot_titles=subplot_titles,
    )

    # --- Row 1: Candlestick ---
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color=COLOR_UP,
            decreasing_line_color=COLOR_DOWN,
            increasing_fillcolor=COLOR_UP,
            decreasing_fillcolor=COLOR_DOWN,
        ),
        row=1, col=1,
    )

    if show_sma and "SMA_20" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["SMA_20"],
                name="SMA 20", mode="lines",
                line=dict(color=COLOR_SMA20, width=1.2),
            ),
            row=1, col=1,
        )
    if show_sma and "SMA_50" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["SMA_50"],
                name="SMA 50", mode="lines",
                line=dict(color=COLOR_SMA50, width=1.2),
            ),
            row=1, col=1,
        )

    # --- Sub-charts ---
    current_row = 2

    if show_rsi and "RSI_14" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["RSI_14"],
                name="RSI", mode="lines",
                line=dict(color=COLOR_RSI, width=1.5),
            ),
            row=current_row, col=1,
        )
        # Overbought / oversold reference lines
        for level, label in [(70, "Overbought"), (30, "Oversold")]:
            fig.add_hline(
                y=level, line_dash="dash",
                line_color="#BDBDBD", line_width=1,
                annotation_text=label,
                annotation_font_size=10,
                row=current_row, col=1,
            )
        fig.update_yaxes(range=[0, 100], row=current_row, col=1)
        current_row += 1

    if show_macd:
        macd_col = next((c for c in df.columns if c.startswith("MACD_") and not c.startswith("MACDs") and not c.startswith("MACDh")), None)
        signal_col = next((c for c in df.columns if c.startswith("MACDs_")), None)
        hist_col = next((c for c in df.columns if c.startswith("MACDh_")), None)

        if macd_col:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df[macd_col],
                    name="MACD", mode="lines",
                    line=dict(color=COLOR_MACD, width=1.5),
                ),
                row=current_row, col=1,
            )
        if signal_col:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df[signal_col],
                    name="Signal", mode="lines",
                    line=dict(color=COLOR_SIGNAL, width=1.5),
                ),
                row=current_row, col=1,
            )
        if hist_col:
            colors = [COLOR_HIST_POS if v >= 0 else COLOR_HIST_NEG for v in df[hist_col].fillna(0)]
            fig.add_trace(
                go.Bar(
                    x=df.index, y=df[hist_col],
                    name="Histogram",
                    marker_color=colors,
                    opacity=0.6,
                ),
                row=current_row, col=1,
            )

    # --- Global layout ---
    fig.update_layout(
        height=600 + (len(sub_charts) * 150),
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(family="Inter, sans-serif", color="#212121"),
        legend=dict(orientation="h", y=1.02, x=0),
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=COLOR_GRID, showgrid=True)
    fig.update_yaxes(gridcolor=COLOR_GRID, showgrid=True)

    return fig
