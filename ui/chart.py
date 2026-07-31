"""
ui/chart.py
Builds interactive Plotly candlestick charts with:
  - All indicator sub-charts (EMA, RSI, CVD, CMF, MACD)
  - Weekend gap removal via rangebreaks (daily timeframe)
  - Drag-to-pan + rangeslider for history navigation
  - Configurable height (compact for grid view)
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Colour palette (Muji-inspired) ─────────────────────────────────────────────
C: dict[str, str] = {
    "up":       "#26A69A",
    "down":     "#EF5350",
    "bg":       "#FFFFFF",
    "grid":     "#F5F5F5",
    "text":     "#424242",
    "rsi":      "#9C27B0",
    "macd":     "#2196F3",
    "sig":      "#FF9800",
    "cvd":      "#00BCD4",
}

# Seven distinct colours for EMA lines (maps to periods in order selected)
EMA_PALETTE: list[str] = [
    "#2196F3",  # blue
    "#FF9800",  # orange
    "#9C27B0",  # purple
    "#E91E63",  # pink
    "#00BCD4",  # cyan
    "#8BC34A",  # light green
    "#FF5722",  # deep orange
]


# ── Internal helpers ────────────────────────────────────────────────────────────

def _subplot_spec(config: dict) -> tuple[int, list[float], list[str]]:
    """
    Determine subplot rows based on enabled indicators.

    Returns:
        (n_rows, row_heights_normalised, sub_titles_for_annotation)
    """
    subs: list[tuple[float, str]] = []
    if config.get("show_cvd"):
        subs.append((0.13, "CVD"))
    if config.get("show_rsi"):
        subs.append((0.13, "RSI (14)"))
    if config.get("show_cmf"):
        subs.append((0.13, "CMF (20)"))
    if config.get("show_macd"):
        f, s, sig = (
            config.get("macd_fast",   12),
            config.get("macd_slow",   26),
            config.get("macd_signal",  9),
        )
        subs.append((0.17, f"MACD ({f},{s},{sig})"))

    spacing     = 0.025 * len(subs)
    main_height = max(0.30, 1.0 - sum(h for h, _ in subs) - spacing)
    heights     = [main_height] + [h for h, _ in subs]
    titles      = [""] + [t for _, t in subs]
    return 1 + len(subs), heights, titles


# ── Public API ──────────────────────────────────────────────────────────────────

def build_chart(
    df: pd.DataFrame,
    title: str,
    config: dict,
    timeframe: str = "Harian",
    height: int = 700,
) -> go.Figure:
    """
    Build a fully interactive Plotly chart.

    Args:
        df:        OHLCV + indicator DataFrame from calculate_indicators().
        title:     Chart title string.
        config:    Indicator config dict (ema_periods, show_rsi, show_macd, …).
        timeframe: 'Harian' | 'Mingguan' | 'Bulanan'
                   Used to decide whether to apply weekend rangebreaks.
        height:    Chart pixel height (use ~420 for grid cells, ~700 for single).

    Returns:
        Plotly Figure ready for st.plotly_chart().
    """
    n_rows, row_heights, sub_titles = _subplot_spec(config)

    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=row_heights,
        #subplot_titles=[""] + sub_titles[1:],   # annotate sub-charts only
    )

    # ── Row 1: Candlestick ────────────────────────────────────────────────────
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],  high=df["High"],
            low=df["Low"],   close=df["Close"],
            name="OHLC",
            increasing_line_color=C["up"],   increasing_fillcolor=C["up"],
            decreasing_line_color=C["down"], decreasing_fillcolor=C["down"],
            line=dict(width=1),
            whiskerwidth=0.8,
        ),
        row=1, col=1,
    )

    # EMA overlays on main chart
    for i, period in enumerate(config.get("ema_periods", [])):
        col_name = f"EMA_{period}"
        if col_name in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df[col_name],
                    name=f"EMA {period}",
                    mode="lines",
                    line=dict(color=EMA_PALETTE[i % len(EMA_PALETTE)], width=1.3),
                    hovertemplate=f"EMA {period}: %{{y:.3f}}<extra></extra>",
                ),
                row=1, col=1,
            )

    # ── Sub-charts ────────────────────────────────────────────────────────────
    cur = 2

    # CVD
    if config.get("show_cvd") and "CVD" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["CVD"],
                name="CVD", mode="lines",
                line=dict(color=C["cvd"], width=1.4),
                fill="tozeroy",
                fillcolor="rgba(0,188,212,0.08)",
            ),
            row=cur, col=1,
        )
        cur += 1

    # RSI
    if config.get("show_rsi") and "RSI_14" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["RSI_14"],
                name="RSI", mode="lines",
                line=dict(color=C["rsi"], width=1.4),
            ),
            row=cur, col=1,
        )
        fig.add_hline(y=70, line_dash="dot", line_color="#EF5350", line_width=1,
                      row=cur, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#26A69A", line_width=1,
                      row=cur, col=1)
        fig.update_yaxes(range=[0, 100], row=cur, col=1)
        cur += 1

    # CMF
    if config.get("show_cmf") and "CMF" in df.columns:
        cmf_vals = df["CMF"].fillna(0)
        cmf_colors = [C["up"] if v >= 0 else C["down"] for v in cmf_vals]
        fig.add_trace(
            go.Bar(
                x=df.index, y=cmf_vals,
                name="CMF",
                marker_color=cmf_colors,
                opacity=0.75,
            ),
            row=cur, col=1,
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#BDBDBD", line_width=1,
                      row=cur, col=1)
        cur += 1

    # MACD
    if config.get("show_macd") and "MACD_line" in df.columns:
        # Histogram (background)
        if "MACD_hist" in df.columns:
            hist_vals = df["MACD_hist"].fillna(0)
            hist_colors = [C["up"] if v >= 0 else C["down"] for v in hist_vals]
            fig.add_trace(
                go.Bar(
                    x=df.index, y=hist_vals,
                    name="Histogram",
                    marker_color=hist_colors,
                    opacity=0.50,
                ),
                row=cur, col=1,
            )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["MACD_line"],
                name="MACD", mode="lines",
                line=dict(color=C["macd"], width=1.4),
            ),
            row=cur, col=1,
        )
        if "MACD_signal" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df["MACD_signal"],
                    name="Signal", mode="lines",
                    line=dict(color=C["sig"], width=1.4),
                ),
                row=cur, col=1,
            )

    # ── Layout ────────────────────────────────────────────────────────────────
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=13, color=C["text"]),
            x=0, xanchor="left",
        ),
        height=height,
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font=dict(family="Inter, sans-serif", size=11, color=C["text"]),
        legend=dict(
            orientation="h", y=1.02, x=0,
            bgcolor="rgba(255,255,255,0.85)",
            font=dict(size=10),
        ),
        margin=dict(l=8, r=8, t=50, b=8),
        hovermode="x unified",
        dragmode="pan",               # left-click drag = pan
        xaxis_rangeslider_visible=False,  # disable default; custom slider below
    )

    # Uniform grid styling across all axes
    fig.update_xaxes(showgrid=True, gridcolor=C["grid"], zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=C["grid"], zeroline=False)

    # Remove Saturday–Sunday gaps for daily charts
    if timeframe == "Harian":
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

    # Rangeslider on the bottom x-axis for drag-based history navigation
    # With shared_xaxes the last row's axis is xaxis{n_rows} (or xaxis if only 1 row)
    bottom_axis = "xaxis" if n_rows == 1 else f"xaxis{n_rows}"
    fig.update_layout(**{
        bottom_axis: dict(
            rangeslider=dict(
                visible=True,
                thickness=0.04,
                bgcolor="#F0F0F0",
            )
        )
    })

    return fig
