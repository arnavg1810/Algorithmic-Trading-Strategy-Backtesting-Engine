"""
Algorithmic Trading Strategy: Moving Average Crossover
Executes the full strategy pipeline and saves outputs.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
import warnings
import os

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 7)
plt.rcParams['font.size'] = 12

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 1. DATA COLLECTION
# ============================================================
TICKER = 'AAPL'
PERIOD = '5y'

print('=' * 70)
print('  ALGORITHMIC TRADING STRATEGY: MOVING AVERAGE CROSSOVER')
print('=' * 70)
print(f'\nTicker: {TICKER}')
print(f'Period: {PERIOD}')
print(f'Downloading data from Yahoo Finance...\n')

raw_data = yf.download(TICKER, period=PERIOD, auto_adjust=True)

print(f'Downloaded {len(raw_data)} trading days of data')
print(f'Date range: {raw_data.index.min().date()} to {raw_data.index.max().date()}')
print(f'\n--- Head of Data ---')
print(raw_data.head(10).to_string())
print(f'\n--- Summary Statistics ---')
print(raw_data.describe().round(2).to_string())
print(f'\nMissing values: {raw_data.isnull().sum().sum()}')

df = raw_data[['Close']].copy()
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[0] for col in df.columns]
df.dropna(inplace=True)
print(f'Cleaned dataframe: {df.shape[0]} rows')

# ============================================================
# 2. STRATEGY LOGIC
# ============================================================
SHORT_WINDOW = 50
LONG_WINDOW = 200

df['SMA_50'] = df['Close'].rolling(window=SHORT_WINDOW, min_periods=SHORT_WINDOW).mean()
df['SMA_200'] = df['Close'].rolling(window=LONG_WINDOW, min_periods=LONG_WINDOW).mean()

df['Signal'] = 0
df.loc[df['SMA_50'] > df['SMA_200'], 'Signal'] = 1
df.loc[df['SMA_50'] < df['SMA_200'], 'Signal'] = -1

df['Crossover'] = df['Signal'].diff()
df['Position'] = df['Signal'].shift(1)

df['Buy_Signal'] = (df['Crossover'] == 2)
df['Sell_Signal'] = (df['Crossover'] == -2)

buy_dates = df[df['Buy_Signal']].index
sell_dates = df[df['Sell_Signal']].index

print(f'\n{"=" * 70}')
print('  TRADING SIGNALS')
print('=' * 70)
print(f'Buy signals:  {len(buy_dates)}')
print(f'Sell signals: {len(sell_dates)}')
print(f'\n--- Buy Signal Dates ---')
for d in buy_dates:
    print(f'  {d.date()}  |  Close: ${df.loc[d, "Close"]:.2f}')
print(f'\n--- Sell Signal Dates ---')
for d in sell_dates:
    print(f'  {d.date()}  |  Close: ${df.loc[d, "Close"]:.2f}')

# ============================================================
# 3. BACKTESTING
# ============================================================
INITIAL_CAPITAL = 100_000

df['Daily_Return'] = df['Close'].pct_change()
df['Strategy_Return'] = df['Daily_Return'] * (df['Position'] == 1).astype(int)
df['BuyHold_Return'] = df['Daily_Return']

df['Strategy_Cumulative'] = (1 + df['Strategy_Return']).cumprod()
df['BuyHold_Cumulative'] = (1 + df['BuyHold_Return']).cumprod()

df['Strategy_Value'] = INITIAL_CAPITAL * df['Strategy_Cumulative']
df['BuyHold_Value'] = INITIAL_CAPITAL * df['BuyHold_Cumulative']

backtest = df.dropna().copy()

print(f'\n{"=" * 70}')
print('  BACKTESTING RESULTS')
print('=' * 70)
print(f'Backtest period: {backtest.index.min().date()} to {backtest.index.max().date()}')
print(f'Trading days:    {len(backtest)}')
print(f'\nFinal Strategy Portfolio Value:    ${backtest["Strategy_Value"].iloc[-1]:>12,.2f}')
print(f'Final Buy-and-Hold Portfolio Value: ${backtest["BuyHold_Value"].iloc[-1]:>12,.2f}')

# ============================================================
# 4. PERFORMANCE ANALYSIS
# ============================================================
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.0

def compute_performance_metrics(returns, label='Strategy'):
    total_return = (1 + returns).prod() - 1
    n_years = len(returns) / TRADING_DAYS_PER_YEAR
    annualized_return = (1 + total_return) ** (1 / n_years) - 1
    annualized_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe_ratio = (annualized_return - RISK_FREE_RATE) / annualized_vol if annualized_vol != 0 else 0

    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    return {
        'Label': label,
        'Total Return (%)': f'{total_return * 100:.2f}%',
        'Annualized Return (%)': f'{annualized_return * 100:.2f}%',
        'Annualized Volatility (%)': f'{annualized_vol * 100:.2f}%',
        'Sharpe Ratio': f'{sharpe_ratio:.3f}',
        'Maximum Drawdown (%)': f'{max_drawdown * 100:.2f}%'
    }

strategy_metrics = compute_performance_metrics(backtest['Strategy_Return'], 'MA Crossover Strategy')
buyhold_metrics = compute_performance_metrics(backtest['BuyHold_Return'], 'Buy & Hold')

metrics_df = pd.DataFrame([strategy_metrics, buyhold_metrics]).set_index('Label')

print(f'\n{"=" * 70}')
print('  PERFORMANCE COMPARISON')
print('=' * 70)
print(metrics_df.to_string())
print('=' * 70)

# ============================================================
# 5. VISUALIZATIONS
# ============================================================

# --- Chart 1: Price with MAs and Signals ---
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(df.index, df['Close'], label='Close Price', color='#333333', linewidth=1.0, alpha=0.9)
ax.plot(df.index, df['SMA_50'], label='50-Day SMA', color='#2196F3', linewidth=1.5, alpha=0.85)
ax.plot(df.index, df['SMA_200'], label='200-Day SMA', color='#FF9800', linewidth=1.5, alpha=0.85)
ax.scatter(df[df['Buy_Signal']].index, df[df['Buy_Signal']]['Close'],
           marker='^', color='#4CAF50', s=140, zorder=5, label='Buy Signal (Golden Cross)', edgecolors='black', linewidths=0.5)
ax.scatter(df[df['Sell_Signal']].index, df[df['Sell_Signal']]['Close'],
           marker='v', color='#F44336', s=140, zorder=5, label='Sell Signal (Death Cross)', edgecolors='black', linewidths=0.5)
ax.set_title(f'{TICKER} — Price Chart with Moving Average Crossover Signals', fontsize=16, fontweight='bold')
ax.set_xlabel('Date', fontsize=13)
ax.set_ylabel('Price (USD)', fontsize=13)
ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '1_price_chart_with_signals.png'), dpi=150, bbox_inches='tight')
plt.close()
print('\nSaved: output/1_price_chart_with_signals.png')

# --- Chart 2: Equity Curve ---
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(backtest.index, backtest['Strategy_Value'], label='MA Crossover Strategy', color='#2196F3', linewidth=2.0)
ax.plot(backtest.index, backtest['BuyHold_Value'], label='Buy & Hold', color='#FF9800', linewidth=2.0, alpha=0.8)
ax.axhline(y=INITIAL_CAPITAL, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
ax.fill_between(backtest.index, backtest['Strategy_Value'], INITIAL_CAPITAL,
                where=backtest['Strategy_Value'] >= INITIAL_CAPITAL, alpha=0.1, color='green')
ax.fill_between(backtest.index, backtest['Strategy_Value'], INITIAL_CAPITAL,
                where=backtest['Strategy_Value'] < INITIAL_CAPITAL, alpha=0.1, color='red')
ax.set_title(f'Equity Curve — Strategy vs Buy & Hold (Initial Capital: ${INITIAL_CAPITAL:,.0f})', fontsize=16, fontweight='bold')
ax.set_xlabel('Date', fontsize=13)
ax.set_ylabel('Portfolio Value (USD)', fontsize=13)
ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
ax.grid(True, alpha=0.3)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '2_equity_curve.png'), dpi=150, bbox_inches='tight')
plt.close()
print('Saved: output/2_equity_curve.png')

# --- Chart 3: Drawdown ---
cumulative = (1 + backtest['Strategy_Return']).cumprod()
running_max = cumulative.cummax()
drawdown = (cumulative - running_max) / running_max

fig, ax = plt.subplots(figsize=(16, 5))
ax.fill_between(drawdown.index, drawdown * 100, 0, color='#F44336', alpha=0.4)
ax.plot(drawdown.index, drawdown * 100, color='#D32F2F', linewidth=1.0)
ax.set_title('Strategy Drawdown Over Time', fontsize=16, fontweight='bold')
ax.set_xlabel('Date', fontsize=13)
ax.set_ylabel('Drawdown (%)', fontsize=13)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '3_drawdown.png'), dpi=150, bbox_inches='tight')
plt.close()
print('Saved: output/3_drawdown.png')

print(f'\nMax Drawdown: {drawdown.min() * 100:.2f}% (at {drawdown.idxmin().date()})')

# ============================================================
# 6. SAVE DATA
# ============================================================
backtest.to_csv(os.path.join(OUTPUT_DIR, 'backtest_data.csv'))
metrics_df.to_csv(os.path.join(OUTPUT_DIR, 'performance_metrics.csv'))
print(f'\nSaved: output/backtest_data.csv')
print(f'Saved: output/performance_metrics.csv')

print(f'\n{"=" * 70}')
print('  PROJECT EXECUTION COMPLETE')
print('=' * 70)
print(f'\nAll outputs saved to: {OUTPUT_DIR}')
print('Open Algorithmic_Trading_Strategy.ipynb in Jupyter for the full report.')
