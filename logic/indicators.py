"""
logic/indicators.py
Calculates technical indicators using pandas-ta.
Accepts a single config dict for all settings.
"""

import pandas as pd
import pandas_ta as ta


def calculate_indicators(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Append selected technical indicators to the OHLCV DataFrame.

    Args:
        df:     OHLCV DataFrame from fetch_stock_data().
        config: Dict with keys:
                  ema_periods  – list[int] e.g. [20, 50]
                  show_rsi     – bool
                  show_macd    – bool
                  macd_fast    – int (default 12)
                  macd_slow    – int (default 26)
                  macd_signal  – int (default 9)
                  show_cvd     – bool
                  show_cmf     – bool

    Returns:
        DataFrame with additional indicator columns appended.
    """
    result = df.copy()

    # ── EMA ───────────────────────────────────────────────────────────────────
    for period in config.get("ema_periods", []):
        try:
            ema = ta.ema(result["Close"], length=int(period))
            if ema is not None:
                result[f"EMA_{period}"] = ema.values
        except Exception:
            pass

    # ── RSI (14) ──────────────────────────────────────────────────────────────
    if config.get("show_rsi"):
        try:
            rsi = ta.rsi(result["Close"], length=14)
            if rsi is not None:
                result["RSI_14"] = rsi.values
        except Exception:
            pass

    # ── MACD (custom fast / slow / signal) ───────────────────────────────────
    if config.get("show_macd"):
        fast   = int(config.get("macd_fast",   12))
        slow   = int(config.get("macd_slow",   26))
        signal = int(config.get("macd_signal",  9))
        try:
            macd_df = ta.macd(result["Close"], fast=fast, slow=slow, signal=signal)
            if macd_df is not None:
                cols     = macd_df.columns.tolist()
                macd_col = next((c for c in cols if c.startswith("MACD_")),  None)
                sig_col  = next((c for c in cols if c.startswith("MACDs_")), None)
                hist_col = next((c for c in cols if c.startswith("MACDh_")), None)
                if macd_col:
                    result["MACD_line"]   = macd_df[macd_col].values
                if sig_col:
                    result["MACD_signal"] = macd_df[sig_col].values
                if hist_col:
                    result["MACD_hist"]   = macd_df[hist_col].values
        except Exception:
            pass

    # ── CVD — Cumulative Volume Delta (approx from candle direction) ──────────
    if config.get("show_cvd"):
        try:
            delta = result["Volume"].astype(float).copy()
            delta[result["Close"] < result["Open"]] *= -1
            result["CVD"] = delta.cumsum()
        except Exception:
            pass

    # ── CMF — Chaikin Money Flow (length 20) ──────────────────────────────────
    if config.get("show_cmf"):
        try:
            cmf = ta.cmf(
                result["High"], result["Low"],
                result["Close"], result["Volume"],
                length=20,
            )
            if cmf is not None:
                result["CMF"] = cmf.values if hasattr(cmf, "values") else cmf
        except Exception:
            pass

    return result
