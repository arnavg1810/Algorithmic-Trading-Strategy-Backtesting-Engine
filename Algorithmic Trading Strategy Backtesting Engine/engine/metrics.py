"""
Performance metrics and trade statistics for backtest results.
"""

import pandas as pd
import numpy as np

TRADING_DAYS_PER_YEAR = 252


def calculate_metrics(returns: pd.Series, label: str = "Strategy") -> dict:
    """Standard performance metrics: total return, ann. return, ann. vol, Sharpe, max drawdown."""
    total_ret = (1 + returns).prod() - 1
    n_years = len(returns) / TRADING_DAYS_PER_YEAR
    ann_ret = (1 + total_ret) ** (1 / n_years) - 1 if n_years > 0 else 0
    ann_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe = (ann_ret / ann_vol) if ann_vol != 0 else 0.0

    cum = (1 + returns).cumprod()
    dd = (cum - cum.cummax()) / cum.cummax()
    max_dd = dd.min()

    return {
        "Label": label,
        "Total Return": total_ret,
        "Annualized Return": ann_ret,
        "Annualized Volatility": ann_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd,
    }


def get_win_rate(backtest_df: pd.DataFrame) -> float:
    """Percentage of invested days with positive strategy return."""
    rets = backtest_df["Strategy_Return"]
    invested = rets[rets != 0]
    if len(invested) == 0:
        return 0.0
    return (invested > 0).sum() / len(invested) * 100


def generate_trade_summary(df_strat: pd.DataFrame, backtest_df: pd.DataFrame) -> dict:
    """
    Trade summary: number of trades, win rate, avg trade return, largest win, largest loss.
    Uses Position changes to count trades; uses Strategy_Return on position-change days for PnL.
    """
    pos = backtest_df["Position"]
    pos_diff = pos.diff()
    # Trade = any position change (entry or exit)
    trade_days = pos_diff[pos_diff != 0].index
    n_trades = len(trade_days)

    rets = backtest_df["Strategy_Return"]
    invested_days = rets[rets != 0]
    win_rate = get_win_rate(backtest_df)

    if len(invested_days) > 0:
        avg_trade_return = invested_days.mean() * 100  # in %
        largest_win = invested_days.max() * 100
        largest_loss = invested_days.min() * 100
    else:
        avg_trade_return = largest_win = largest_loss = 0.0

    return {
        "num_trades": n_trades,
        "win_rate": win_rate,
        "avg_trade_return_pct": avg_trade_return,
        "largest_win_pct": largest_win,
        "largest_loss_pct": largest_loss,
    }
