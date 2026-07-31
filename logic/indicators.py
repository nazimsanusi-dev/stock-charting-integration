"""
logic/indicators.py
Calculates technical indicators (SMA, RSI, MACD) using pandas-ta.
"""

import pandas as pd
import pandas_ta as ta


def calculate_indicators(
    df: pd.DataFrame,
    show_sma: bool = True,
    show_rsi: bool = True,
    show_macd: bool = True,
) -> pd.DataFrame:
    """
    Append selected technical indicators to the OHLCV DataFrame.

    Args:
        df: OHLCV DataFrame from fetch_stock_data().
        show_sma: Whether to calculate SMA (20 and 50 periods).
        show_rsi: Whether to calculate RSI (14 periods).
        show_macd: Whether to calculate MACD (12, 26, 9).

    Returns:
        DataFrame with additional indicator columns appended.
    """
    result = df.copy()

    if show_sma:
        result["SMA_20"] = ta.sma(result["Close"], length=20)
        result["SMA_50"] = ta.sma(result["Close"], length=50)

    if show_rsi:
        result["RSI_14"] = ta.rsi(result["Close"], length=14)

    if show_macd:
        macd_df = ta.macd(result["Close"], fast=12, slow=26, signal=9)
        if macd_df is not None:
            result = pd.concat([result, macd_df], axis=1)

    return result
