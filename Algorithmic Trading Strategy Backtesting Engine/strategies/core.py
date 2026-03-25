"""
Modular strategy functions. Each returns a dataframe with:
- Close, Signal, Position (shifted by 1 to avoid look-ahead bias).
- Strategy-specific columns (e.g. SMA_Short, SMA_Long, RSI) for charts and regime.
"""

import pandas as pd
import numpy as np
from .indicators import rsi


def moving_average_crossover(
    df: pd.DataFrame, short_window: int, long_window: int
) -> pd.DataFrame:
    """
    Moving Average Crossover: Buy when short MA > long MA, Sell when short MA < long MA.
    Returns dataframe with Signal, Position (shifted), SMA_Short, SMA_Long, Crossover, Buy_Signal, Sell_Signal.
    """
    out = df[["Close"]].copy()
    out["SMA_Short"] = out["Close"].rolling(window=short_window, min_periods=short_window).mean()
    out["SMA_Long"] = out["Close"].rolling(window=long_window, min_periods=long_window).mean()

    out["Signal"] = 0
    out.loc[out["SMA_Short"] > out["SMA_Long"], "Signal"] = 1
    out.loc[out["SMA_Short"] < out["SMA_Long"], "Signal"] = -1

    out["Crossover"] = out["Signal"].diff()
    out["Position"] = out["Signal"].shift(1)
    out["Buy_Signal"] = out["Crossover"] == 2
    out["Sell_Signal"] = out["Crossover"] == -2
    return out


def moving_average_rsi(
    df: pd.DataFrame,
    short_window: int,
    long_window: int,
    rsi_period: int = 14,
) -> pd.DataFrame:
    """
    MA + RSI: Buy when Short MA > Long MA AND RSI > 50; Sell when Short MA < Long MA AND RSI < 50.
    """
    out = df[["Close"]].copy()
    out["SMA_Short"] = out["Close"].rolling(window=short_window, min_periods=short_window).mean()
    out["SMA_Long"] = out["Close"].rolling(window=long_window, min_periods=long_window).mean()
    out["RSI"] = rsi(out["Close"], rsi_period)

    out["Signal"] = 0
    buy_cond = (out["SMA_Short"] > out["SMA_Long"]) & (out["RSI"] > 50)
    sell_cond = (out["SMA_Short"] < out["SMA_Long"]) & (out["RSI"] < 50)
    out.loc[buy_cond, "Signal"] = 1
    out.loc[sell_cond, "Signal"] = -1
    # If neither: keep previous signal (forward fill after first valid)
    out["Signal"] = out["Signal"].replace(0, np.nan).ffill().fillna(0).astype(int)

    out["Crossover"] = out["Signal"].diff()
    out["Position"] = out["Signal"].shift(1)
    out["Buy_Signal"] = out["Crossover"] == 2
    out["Sell_Signal"] = out["Crossover"] == -2
    return out


def rsi_only(df: pd.DataFrame, rsi_period: int = 14) -> pd.DataFrame:
    """
    RSI Only: Buy when RSI < 30 (oversold), Sell when RSI > 70 (overbought).
    """
    out = df[["Close"]].copy()
    out["RSI"] = rsi(out["Close"], rsi_period)

    out["Signal"] = 0
    out.loc[out["RSI"] < 30, "Signal"] = 1
    out.loc[out["RSI"] > 70, "Signal"] = -1
    out["Signal"] = out["Signal"].replace(0, np.nan).ffill().fillna(0).astype(int)

    out["Crossover"] = out["Signal"].diff()
    out["Position"] = out["Signal"].shift(1)
    out["Buy_Signal"] = out["Crossover"] == 2
    out["Sell_Signal"] = out["Crossover"] == -2
    return out


def buy_and_hold(df: pd.DataFrame) -> pd.DataFrame:
    """
    Buy & Hold: Always invested (Position = 1). No crossover signals.
    """
    out = df[["Close"]].copy()
    out["Signal"] = 1
    out["Position"] = 1
    out["Buy_Signal"] = False
    out["Sell_Signal"] = False
    out["Crossover"] = 0
    return out


# Strategy registry for the router
STRATEGIES = {
    "Moving Average Crossover": moving_average_crossover,
    "MA + RSI": moving_average_rsi,
    "RSI Only": rsi_only,
    "Buy & Hold": buy_and_hold,
}


def apply_strategy(
    df: pd.DataFrame,
    strategy_type: str,
    params: dict,
) -> pd.DataFrame:
    """
    Router: apply the selected strategy with given parameters.
    Returns dataframe with Signal and Position (and strategy-specific columns).
    """
    if strategy_type not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_type}. Choose from {list(STRATEGIES.keys())}")

    fn = STRATEGIES[strategy_type]
    if strategy_type == "Moving Average Crossover":
        return fn(df, params["short_window"], params["long_window"])
    if strategy_type == "MA + RSI":
        return fn(
            df,
            params["short_window"],
            params["long_window"],
            params.get("rsi_period", 14),
        )
    if strategy_type == "RSI Only":
        return fn(df, params.get("rsi_period", 14))
    if strategy_type == "Buy & Hold":
        return fn(df)
    return fn(df, **{k: v for k, v in params.items() if k in ["short_window", "long_window", "rsi_period"]})
