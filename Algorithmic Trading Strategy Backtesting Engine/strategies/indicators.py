"""
Reusable technical indicators for strategy modules.
Uses rolling average method for gains/losses (Wilder-style RSI).
"""

import pandas as pd
import numpy as np


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index using rolling average of gains and losses.
    RSI = 100 - (100 / (1 + RS)) where RS = avg_gain / avg_loss.
    """
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = np.where(avg_loss == 0, np.inf, avg_gain / avg_loss)
    rsi_series = 100 - (100 / (1 + rs))
    return pd.Series(rsi_series, index=close.index)
