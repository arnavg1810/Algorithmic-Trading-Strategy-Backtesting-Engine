"""
Backtest engine: applies position to daily returns, optional transaction costs.
Cost is applied only when position changes: cost = abs(position.diff()) * transaction_cost (as decimal).
"""

import pandas as pd
import numpy as np

TRADING_DAYS_PER_YEAR = 252


def backtest_strategy(
    df: pd.DataFrame,
    initial_capital: float,
    transaction_cost_pct: float = 0.0,
    use_transaction_cost: bool = False,
) -> pd.DataFrame:
    """
    Run backtest: strategy return = daily return * position (1 when long, 0 when flat/cash).
    If use_transaction_cost: deduct cost only on position change days.
    Cost per trade = transaction_cost_pct / 100 (e.g. 0.1% -> 0.001).
    """
    out = df[["Close", "Position"]].copy()
    out["Daily_Return"] = out["Close"].pct_change()
    # Strategy return: only earn when position == 1 (long)
    position_active = (out["Position"] == 1).astype(int)
    out["Strategy_Return"] = out["Daily_Return"] * position_active
    out["BuyHold_Return"] = out["Daily_Return"]

    if use_transaction_cost and transaction_cost_pct != 0:
        cost_decimal = transaction_cost_pct / 100.0
        position_changes = out["Position"].diff().abs()
        # Cost only when position actually changes (entry or exit)
        trade_cost = position_changes * cost_decimal
        out["Strategy_Return"] = out["Strategy_Return"] - trade_cost

    out["Strategy_Cumulative"] = (1 + out["Strategy_Return"]).cumprod()
    out["BuyHold_Cumulative"] = (1 + out["BuyHold_Return"]).cumprod()
    out["Strategy_Value"] = initial_capital * out["Strategy_Cumulative"]
    out["BuyHold_Value"] = initial_capital * out["BuyHold_Cumulative"]
    return out.dropna(subset=["Strategy_Return"])
