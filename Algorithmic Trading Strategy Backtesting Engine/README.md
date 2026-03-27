# Multi-Strategy Quantitative Trading Dashboard

An interactive web application that implements, backtests, and visualizes **multiple algorithmic trading strategies** on real historical stock data from global markets. Built with **Streamlit**, **Plotly**, and **yfinance** for a professional, dashboard-style experience with support for **4 distinct trading strategies** and **5 major global indices**.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Trading Strategies](#2-trading-strategies)
3. [How the Strategies Work](#3-how-the-strategies-work)
4. [Application Architecture](#4-application-architecture)
5. [File Structure](#5-file-structure)
6. [Setup & Installation](#6-setup--installation)
7. [How to Run](#7-how-to-run)
8. [Application Walkthrough (8 Tabs)](#8-application-walkthrough-8-tabs)
9. [Supported Markets & Indices](#9-supported-markets--indices)
10. [Functional Features](#10-functional-features)
11. [Non-Functional Features](#11-non-functional-features)
12. [Advanced Features](#12-advanced-features)
13. [Known Limitations](#13-known-limitations)
14. [Future Enhancements & Roadmap](#14-future-enhancements--roadmap)
15. [Tech Stack](#15-tech-stack)
16. [Key Functions Reference](#16-key-functions-reference)
17. [Module Reference](#17-module-reference)
18. [License & Disclaimer](#18-license--disclaimer)

---

## 1. Project Overview

### What Is This Project?

This project is an **enterprise-grade quantitative finance tool** that lets users explore, backtest, and evaluate **multiple algorithmic trading strategies** entirely through an interactive web interface. It downloads live market data from global exchanges, computes trading signals using various technical indicators, simulates portfolio performance, calculates institutional-grade performance metrics, and renders interactive charts — all in real time as the user adjusts parameters.

### Who Is It For?

- **Finance & MBA students** learning algorithmic trading concepts
- **Aspiring quantitative analysts** building professional portfolio projects
- **Active traders** exploring systematic strategies before risking real capital
- **Hedge fund professionals** backtesting multi-strategy approaches
- **Educators** demonstrating backtesting methodology in classroom settings
- **Developers** looking for a clean, modular Streamlit + Plotly enterprise reference project

### What Problem Does It Solve?

Most backtesting tutorials are static Jupyter notebooks with hardcoded parameters and single strategies. This project converts that static workflow into a **live, interactive dashboard** where users can:
- Choose from **4 distinct trading strategies** (MA Crossover, MA+RSI, RSI Only, Buy & Hold)
- Trade on **5 major global indices** (Nifty 50, BSE Sensex, S&P 500, Nasdaq 100, Dow Jones) or any custom ticker
- Tune parameters and see results update in real time
- Model transaction costs to understand real-world impact
- Compare strategy returns against multiple passive benchmarks
- Understand performance through professional metrics (Sharpe Ratio, Max Drawdown, Win Rate, etc.)

---

## 2. Trading Strategies

### Four Distinct Algorithmic Trading Strategies

The application now supports **4 independent trading strategies**, each with distinct entry/exit logic and characteristics:

| Strategy | Entry Signal | Exit Signal | Best For | Indicators Used |
|----------|--------------|------------|----------|-----------------|
| **MA Crossover** | Short MA crosses above Long MA (Golden Cross) | Short MA crosses below Long MA (Death Cross) | Trend-following, medium hold periods | SMA_Short, SMA_Long |
| **MA + RSI** | Short MA > Long MA **AND** RSI > 50 | Short MA < Long MA **AND** RSI < 50 | Momentum confirmation, reduced false signals | SMA_Short, SMA_Long, RSI |
| **RSI Only** | RSI < 30 (oversold) | RSI > 70 (overbought) | Mean-reversion, oscillator-based | RSI |
| **Buy & Hold** | Always invested (Day 1) | Never (hold forever) | Benchmark for comparison | None |

### Strategy Selection

Users can select their preferred strategy from a dropdown in the Streamlit sidebar. Each strategy generates its own:
- Trading signals (Buy/Sell)
- Position vectors (1 = long, 0 = flat)
- Performance metrics
- Interactive charts with signal markers

---

## 3. How the Strategies Work

### Strategy 1: Moving Average Crossover (Classic Trend-Following)

A **Moving Average (MA)** smooths price data by calculating the average closing price over a rolling window of *N* days. By using two MAs with different lookback periods, we can detect changes in trend direction:

| Component | Default | Role |
|-----------|---------|------|
| **Short-term MA** | 50-day SMA | Captures recent momentum; reacts quickly to price changes |
| **Long-term MA** | 200-day SMA | Reflects the broader trend; filters out short-term noise |

#### Trading Signals

| Event | Condition | Action |
|-------|-----------|--------|
| **Golden Cross** | Short MA crosses **above** Long MA | **Buy** — uptrend is forming |
| **Death Cross** | Short MA crosses **below** Long MA | **Sell** — downtrend is forming |

#### Signal Pipeline (step by step)

```
Raw Price Data
    │
    ▼
Compute SMA_Short (e.g., 50-day rolling mean)
Compute SMA_Long  (e.g., 200-day rolling mean)
    │
    ▼
Generate Signal Column:
    +1 when SMA_Short > SMA_Long
    -1 when SMA_Short < SMA_Long
     0 when equal
    │
    ▼
Detect Crossovers (Signal.diff() == ±2)
    │
    ▼
Shift Position by 1 day (prevent look-ahead bias)
    │
    ▼
Backtest: multiply daily returns by position
    │
    ▼
Compute cumulative returns, equity curve, metrics
```

### Strategy 2: MA + RSI (Momentum-Filtered Trend-Following)

This strategy enhances the MA Crossover by adding an **RSI (Relative Strength Index)** confirmation filter to reduce false signals in choppy markets.

**RSI Concept:** RSI measures momentum on a scale of 0–100:
- **RSI < 30**: Oversold — strong downward momentum
- **RSI > 70**: Overbought — strong upward momentum  
- **RSI 30–70**: Neutral zone

#### Trading Signals

| Event | Condition | Action |
|-------|-----------|--------|
| **BUY** | Short MA > Long MA **AND** RSI > 50 | Trend up confirmed by momentum |
| **SELL** | Short MA < Long MA **AND** RSI < 50 | Trend down confirmed by momentum |
| **HOLD** | Either condition fails | Stay in current position or flat |

### Strategy 3: RSI Only (Mean-Reversion / Oscillator-Based)

This is a **pure momentum strategy** that trades based on RSI extremes without moving averages. It assumes that extreme readings (oversold/overbought) mean-revert.

#### Trading Signals

| Event | Condition | Action |
|-------|-----------|--------|
| **BUY** | RSI < 30 | Oversold — expect bounce |
| **SELL** | RSI > 70 | Overbought — expect pullback |
| **HOLD** | RSI between 30–70 | Neutral zone, stay flat or hold |

### Strategy 4: Buy & Hold (Passive Benchmark)

Always fully invested. This is the **benchmark** against which active strategies are compared. Useful for understanding the value added (or lost) by active management.

#### Benefits of Multiple Strategies

1. **Compare Effectiveness** — See which strategy performs best on your chosen ticker
2. **Learn Different Approaches** — Trend-following vs mean-reversion vs passive
3. **Risk Adjustment** — Some strategies are "smoother" (lower drawdown) than others
4. **Market Regime Sensitivity** — Different strategies work in different market conditions (TBD: regime detector)

---

## 4. Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                    │
│                                                         │
│  ┌──────────┐   ┌──────────────────────────────────┐   │
│  │ SIDEBAR  │   │           MAIN AREA              │   │
│  │          │   │                                    │   │
│  │ • Index  │   │  ┌─────┬──────┬─────┬──────────┐ │   │
│  │ • Dates  │   │  │Tab 1│Tab 2 │ ... │  Tab 8   │ │   │
│  │ • Strategy │  │  ├─────┴──────┴─────┴──────────┤ │   │
│  │ • Params │   │  │                              │ │   │
│  │ • Capital│   │  │  Dynamic content rendered    │ │   │
│  │ • Costs  │   │  │  based on active tab          │ │   │
│  │ [RUN]    │   │  │                              │ │   │
│  └──────────┘   │  └──────────────────────────────┘ │   │
│                  └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────────────────┐
│  YAHOO FINANCE  │    │   COMPUTATION LAYER         │
│   (yfinance)    │    │                             │
│                 │    │  strategies/core.py         │
│  Live OHLCV     │───▶│  engine/backtest.py         │
│  data download  │    │  engine/metrics.py          │
│                 │    │  strategies/indicators.py   │
└─────────────────┘    └─────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  VISUALIZATION LAYER │
                    │                      │
                    │  Plotly (interactive) │
                    │  • Price + MA chart   │
                    │  • Equity curve       │
                    │  • Drawdown chart     │
                    │  • Return histograms  │
                    └─────────────────────┘
```

### Data Flow

1. **User configures** parameters in the sidebar (index/ticker, strategy, dates, parameters, capital, costs).
2. **`download_data()`** from app.py fetches OHLCV data from Yahoo Finance and caches it.
3. **`apply_strategy()`** from `strategies/core.py` computes trading signals based on strategy choice.
4. **`backtest_strategy()`** from `engine/backtest.py` simulates portfolio value over time using returns × position.
5. **`calculate_metrics()` & `generate_trade_summary()`** from `engine/metrics.py` compute Sharpe Ratio, drawdown, win rate, etc.
6. **Plotly charts** and **Streamlit components** render everything across 8 tabs with real-time updates.

---

## 5. File Structure

```
P1/
├── app.py                              # Main interactive Streamlit web application
├── run_strategy.py                     # CLI script — runs strategy and saves outputs to output/
├── Algorithmic_Trading_Strategy.ipynb  # Jupyter notebook version with full report
├── requirements.txt                    # Python package dependencies
├── README.md                           # This documentation file
├── data/                               # Market data and index definitions
│   ├── __init__.py
│   └── index_constituents.py           # Nifty 50, Sensex, S&P 500, Nasdaq 100, Dow Jones symbols
├── strategies/                         # Trading strategy implementations (modular)
│   ├── __init__.py
│   ├── core.py                         # Strategy router: MA Crossover, MA+RSI, RSI Only, Buy&Hold
│   └── indicators.py                   # Technical indicators: RSI, SMAs (reusable)
├── engine/                             # Backtesting & metrics computation
│   ├── __init__.py
│   ├── backtest.py                     # Core backtest loop with optional transaction costs
│   └── metrics.py                      # Performance metrics: Sharpe, drawdown, win rate, trade stats
└── output/                             # Generated by run_strategy.py
    ├── backtest_data.csv               # Full backtest results with strategy/B&H returns
    └── performance_metrics.csv         # Summary metrics table
```

| File / Directory | Purpose | When to Use |
|---|---------|-------------|
| `app.py` | Interactive dashboard with live controls and 4 strategies | Primary usage — launch with `streamlit run app.py` |
| `run_strategy.py` | Headless script that prints results and saves CSV to `output/` | Quick CLI execution without a browser |
| `data/index_constituents.py` | Predefined lists of Nifty, Sensex, S&P 500, Nasdaq, Dow symbols | Automatically used by app for dropdown menu |
| `strategies/core.py` | Router and implementations of 4 trading strategies | Core business logic |
| `strategies/indicators.py` | Reusable technical indicators (RSI, SMA) | Used by strategy functions |
| `engine/backtest.py` | Portfolio simulation with position × returns multiplication | Core backtesting engine |
| `engine/metrics.py` | Calculation of Sharpe, Drawdown, Win Rate, trade statistics | Performance evaluation |
| `*.ipynb` | Static notebook with markdown and inline plots | Jupyter / academic submission |
| `requirements.txt` | Pinned minimum versions for all dependencies | Run `pip install -r requirements.txt` before first use |

---

## 6. Setup & Installation

### Prerequisites

- **Python 3.10+** (tested on 3.12)
- **pip** package manager
- Internet connection (to download stock data from Yahoo Finance)

### Step-by-step

```bash
# Clone or navigate to the project directory
cd P1

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install all dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | >= 1.30.0 | Web application framework |
| `plotly` | >= 5.18.0 | Interactive charting library |
| `yfinance` | >= 0.2.31 | Yahoo Finance data API |
| `pandas` | >= 2.0.0 | Data manipulation and analysis |
| `numpy` | >= 1.24.0 | Numerical computations |
| `matplotlib` | >= 3.7.0 | Static charts (used in notebook & CLI script) |
| `jupyter` | >= 1.0.0 | Notebook execution |

---

## 7. How to Run

### Option A — Interactive Web App (Recommended)

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**.

**Workflow:**
1. **Sidebar Configuration:**
   - Select an **Index** (Nifty 50, S&P 500, etc.) or enter a custom ticker
   - Choose **Date Range** (default: last 5 years)
   - Select **Strategy**: MA Crossover, MA+RSI, RSI Only, or Buy & Hold
   - Set **Strategy Parameters**: MA windows, RSI period (based on selected strategy)
   - Toggle **Transaction Costs** and set percentage (optional)
   - Enter **Starting Capital** (default: $100,000)
   - Click **Run Strategy**

2. **View Results:**
   - Wait 2–3 seconds for backtest to complete
   - Navigate through 8 tabs to explore results

### Option B — Command-Line Script

```bash
python run_strategy.py
```

Prints all results to the terminal and saves CSV files to the `output/` folder. Useful for batch runs or CI/CD integration (no browser required).

### Option C — Jupyter Notebook

```bash
jupyter notebook Algorithmic_Trading_Strategy.ipynb
```

Run cells sequentially for a static, report-style walkthrough. Good for academic submissions or creating a detailed written report.

---

### Sidebar Controls (Configuration Guide)

| Control | Type | Options | Default | Purpose |
|---------|------|---------|---------|---------|
| **Index / Ticker** | Dropdown + Text | Nifty 50 / Sensex / S&P 500 / Nasdaq / Dow / Custom | AAPL | Choose market to backtest |
| **Strategy** | Radio/Dropdown | MA Crossover, MA+RSI, RSI Only, Buy & Hold | MA Crossover | Select trading approach |
| **Start Date** | Date Picker | Any past date | 5 years ago | Data start point |
| **End Date** | Date Picker | Any past date ≥ Start Date | Today | Data end point |
| **Short MA** | Slider | 5–100 (step 5), or RSI period for RSI-based | 50 | First trend indicator window |
| **Long MA** | Slider | 50–400 (step 10), or—for RSI Only | 200 | Second trend indicator window |
| **RSI Period** | Slider | 5–50 (if MA+RSI or RSI Only selected) | 14 | RSI momentum window |
| **Starting Capital** | Number | $1,000 – $10,000,000 | $100,000 | Portfolio starting value |
| **Transaction Costs** | Toggle | On / Off | Off | Enable cost modeling |
| **Cost %** | Number | 0.01 – 1.0 | 0.1 | Cost per trade (%) |
| **Run Strategy** | Button | — | — | Execute backtest |

---

## 8. Application Walkthrough (8 Tabs)

### Tab 1 — Introduction

Provides educational context for the selected strategy:
- **What is Algorithmic Trading** — definition, who uses it, why it matters.
- **Selected Strategy Explanation** — dynamic content based on user's chosen strategy:
  - **MA Crossover:** How Golden Cross and Death Cross work, with user's MA windows highlighted.
  - **MA + RSI:** Explanation of both indicators and how RSI filters MA signals.
  - **RSI Only:** Explanation of overbought/oversold conditions and mean-reversion.
  - **Buy & Hold:** Explanation of passive benchmark strategy.
- **Why It Works** — trend-following, momentum, mean-reversion concepts as applicable.

### Tab 2 — Data Collection

Displays downloaded market data:
- **Summary metrics** — total trading days, date range, data source (Yahoo Finance).
- **First 10 rows** — scrollable OHLCV dataframe from downloaded data.
- **Summary statistics** — mean, std, min, max, quartiles via `df.describe()`.
- **Data quality check** — green success badge if no missing values, yellow warning if gaps detected.

### Tab 3 — Strategy Logic

Shows how trading signals are generated for the selected strategy:

**For MA Crossover:**
- **Markdown explanation** — MA computation, crossover detection method, look-ahead bias prevention.
- **Buy signal table** — dates and close prices of Golden Crosses.
- **Sell signal table** — dates and close prices of Death Crosses.

**For MA + RSI:**
- **Markdown explanation** — MA concepts, RSI interpretation (oversold/overbought), combined logic.
- **Buy signal table** — dates of buy signals (MA crossed up AND RSI > 50).
- **Sell signal table** — dates of sell signals (MA crossed down AND RSI < 50).

**For RSI Only:**
- **Markdown explanation** — RSI levels, mean-reversion concept.
- **Buy signal table** — dates when RSI < 30 (entry points).
- **Sell signal table** — dates when RSI > 70 (exit points).

**For Buy & Hold:**
- **Markdown explanation** — passive benchmark concept.
- No entry/exit signals.

- **DataFrame preview** — first 20 rows: Close, SMA_Short (if applicable), SMA_Long (if applicable), RSI (if applicable), Signal, Crossover, Position, Buy_Signal, Sell_Signal.

### Tab 4 — Backtesting

Simulates portfolio performance:
- **Assumptions box** — clearly states transaction costs model (on/off), no slippage, no taxes, perfect execution.
- **Three metric cards:**
  - **Strategy Final Value** — portfolio value at end of backtest period
  - **Buy & Hold Final Value** — passive benchmark value
  - **Gross Profit** — dollar difference (color-coded green if strategy wins, red if loses)
- **Daily returns histogram** — side-by-side histograms (Strategy vs Buy & Hold) showing distribution using Plotly subplots.
- **Trade count summary** — "Made X trades over Y days" to show strategy frequency.

### Tab 5 — Performance Analysis

Institutional-grade metrics in **two rows of 5 cards each:**

**Row 1 (Strategy Metrics):**
- **Total Return** — Overall cumulative profit/loss as percentage
- **Annualized Return** — Average yearly return
- **Annualized Volatility** — Yearly fluctuation magnitude
- **Sharpe Ratio** — Risk-adjusted return (higher is better)
- **Max Drawdown** — Worst peak-to-trough decline
- Each card turns **green** if strategy beats Buy & Hold on that metric

**Row 2 (Buy & Hold Metrics):**
- Same 5 metrics for the benchmark for direct comparison
- Cards display in neutral color (not compared)

- **Expandable explanations** — each metric has a collapsible section explaining what it means in plain financial language.
- **Win Rate Card** — percentage of invested days with positive strategy returns.

### Tab 6 — Interactive Charts

Three professional Plotly visualizations, all interactive (zoom, pan, hover):

1. **Price Chart with Crossover Signals**
   - Close price line (grey)
   - Short MA line (blue) — shows for MA-based strategies
   - Long MA line (orange) — shows for MA-based strategies
   - Green triangle-up markers at every buy signal
   - Red triangle-down markers at every sell signal
   - Unified hover showing all values simultaneously
   - For RSI-only strategy: only price + signals shown (no MAs)

2. **Equity Curve**
   - Strategy portfolio value (blue line with subtle fill)
   - Buy & Hold portfolio value (orange line)
   - Dashed horizontal line at initial capital (reference)
   - Unified hover showing both values at each date
   - Zooming / panning fully supported

3. **Drawdown Chart**
   - Red area fill showing drawdown percentage over time
   - Peak-to-trough decline clearly visible
   - Max drawdown value and date annotated
   - Useful for understanding worst-case risk scenarios

### Tab 7 — Key Insights

Seven auto-generated insights that **adapt to the actual backtest results and strategy type**:

1. **Trend Capture Effectiveness** — How well the strategy captures trending markets (more relevant for trend-following strategies).
2. **Sideways Market Underperformance** — Recognition that trend-following can lag in ranging markets.
3. **Drawdown Protection** — Dynamically compares strategy vs B&H max drawdowns with actionable verdict.
4. **Signal Frequency Analysis** — Reports exact count of buy/sell signals and average hold duration.
5. **Risk-Adjusted Returns** — Compares Sharpe Ratios with a verdict: "Strategy delivers superior..." or "Buy & Hold achieved better...".
6. **Trade Statistics** — Shows win rate, avg trade return, largest win/loss with interpretation.
7. **Strategy Suitability** — Context-aware assessment (e.g., "RSI-only suitable for ranging markets" vs "MA crossover best for strong trends").

Each insight uses live computed values and conditional language based on strategy choice and actual performance.

### Tab 8 — Limitations

Seven+ clearly stated assumptions and limitations:
1. **No transaction costs** (or detailed cost model if enabled)
2. **No slippage** — execution assumed at closing price
3. **No intraday modeling** — daily bars only
4. **Single-indicator reliance** — ignores volume, fundamentals, sentiment
5. **Past ≠ Future** — historical results not predicative
6. **Survivorship bias** — only tests liquid Yahoo Finance tickers
7. **No adaptive money management** — fixed position size, no stops, no risk scaling
8. (Strategy-specific) — e.g., "MA crossover generates false signals in choppy markets"

---

## 10. Functional Features

These are the directly usable, user-facing capabilities of the application.

| Feature | Description |
|---------|-------------|
| F1 | **Multi-Strategy Support** | Choose from 4 pre-built strategies: MA Crossover, MA+RSI, RSI Only, Buy & Hold. Each included in tab for easy comparison. |
| F2 | **Global Market Coverage** | Supports 5 major indices (Nifty 50, BSE Sensex, S&P 500, Nasdaq 100, Dow Jones) plus any custom Yahoo Finance ticker symbol worldwide. |
| F3 | **Live Stock Data Download** | Fetches real-time historical OHLCV data from Yahoo Finance for any valid ticker (US, Indian, European, ETFs, crypto). |
| F4 | **Configurable Trading Parameters** | Adjust strategy-specific parameters: for MA Crossover (Short MA window, Long MA window); for RSI-based strategies (RSI period). |
| F5 | **Custom Date Range Selection** | Pick any start and end date using calendar widgets. Defaults to most recent 5 years. |
| F6 | **Parameter Validation** | Prevents invalid configurations (e.g., Short MA >= Long MA) with inline error messages. |
| F7 | **Configurable Initial Capital** | Number input from $1,000 to $10,000,000. Default: $100,000. |
| F8 | **Transaction Cost Modeling** | Optional toggle to enable transaction costs as a percentage (e.g., 0.1%). Costs applied only on position-change days. |
| F9 | **Moving Average Computation** | Calculates Simple Moving Averages (SMA) using pandas rolling windows with proper `min_periods` to avoid partial-window artifacts. |
| F10 | **RSI Indicator** | Implements Wilder-style RSI (Relative Strength Index) using rolling average method for momentum assessment. |
| F11 | **Signal Generation** | Produces +1 (buy), -1 (sell), 0 (hold) signals based on strategy-specific rules. |
| F12 | **Crossover Detection** | Identifies buy/sell crossover events by detecting signal transitions (magnitude 2 for MA strategies). |
| F13 | **Look-Ahead Bias Prevention** | Position column is shifted by 1 day so signals at close of day *t* are only acted upon at day *t+1*. |
| F14 | **Portfolio Backtesting** | Simulates daily portfolio value by multiplying daily returns by position vector. Optional transaction cost deduction. |
| F15 | **Multi-Benchmark Comparison** | Computes Buy-and-Hold equity curve for direct comparison with active strategies. |
| F16 | **Advanced Performance Metrics** | Computes: Total Return, Annualized Return, Annualized Volatility, Sharpe Ratio, Maximum Drawdown, Win Rate. |
| F17 | **Trade Statistics** | Reports number of trades, win rate (% of profitable days), avg trade return, largest win, largest loss. |
| F18 | **Color-Coded Metric Cards** | Strategy metrics turn green when outperforming Buy & Hold, red when underperforming, for instant visual comparison. |
| F19 | **Interactive Price Chart** | Plotly chart with close price, both MAs (for MA strategies), and buy/sell signal markers. Full zoom, pan, hover, box/lasso select. |
| F20 | **Interactive Equity Curve** | Plotly chart comparing strategy vs buy-and-hold portfolio values with initial capital reference line and unified hover. |
| F21 | **Drawdown Visualization** | Plotly area chart showing strategy drawdown percentage over time with max drawdown annotation. |
| F22 | **Return Distribution Histograms** | Side-by-side histograms of daily returns for strategy vs buy-and-hold using Plotly subplots. |
| F23 | **Buy/Sell Signal Tables** | Tabular display of every buy/sell signal date with corresponding close price and RSI (if applicable). |
| F24 | **Strategy DataFrame Preview** | Shows first 20 rows of computed columns (Close, SMA_Short, SMA_Long, RSI, Signal, Crossover, Position) for transparency. |
| F25 | **Raw Data Display** | Shows first 10 rows and summary statistics of downloaded data with missing value check and data quality badge. |
| F26 | **Educational Content** | Introduction tab explains algo trading, each strategy concept, entry/exit logic, and trend-following vs mean-reversion. |
| F27 | **Metric Explanations** | Expandable sections explain each performance metric in plain financial language with context. |
| F28 | **Limitations Disclosure** | 7+ clearly stated backtest assumptions (no costs, no slippage, perfect execution, past ≠ future). |
| F29 | **Multi-Format Output** | Three delivery formats: interactive web app (Streamlit), CLI script (terminal + CSV), and Jupyter notebook. |
| F30 | **Strategy Strategy Comparison** | Run all 4 strategies on the same ticker/dates instantly and compare metrics side-by-side. |

---

## 11. Non-Functional Features

These are the quality attributes, design decisions, and technical properties that define how the system performs rather than what it does.

| # | Attribute | Description |
|---|-----------|-------------|
| NF1 | **Data Caching** | `@st.cache_data` decorator caches downloaded data so repeated runs with same ticker/dates are instant (no redundant API calls). |
| NF2 | **Responsive Layout** | Streamlit's `layout="wide"` mode with column-based layouts ensures dashboard works on various screen sizes. |
| NF3 | **Premium Dark Theme** | Custom CSS with gradient backgrounds (#0a0e14 → #111820), styled metric cards, and transparent Plotly backgrounds. |
| NF4 | **Custom Typography** | Google Fonts integration: 'Outfit' for headers (modern, geometric), 'JetBrains Mono' for data (clean, readable mono). |
| NF5 | **Hover Animations** | Metric cards have subtle `translateY(-2px)` hover effect with smooth transitions for visual polish and interactivity. |
| NF6 | **Professional Color Palette** | Distinctive amber/cyan accent colors (#e6a23c, #4fc3f7) with muted greys and semantic red/green for contrast. |
| NF7 | **Performance Optimized** | Data download, strategy computation, backtesting, and chart rendering complete in < 3 seconds for typical 5-year dataset (~1,260 points). |
| NF8 | **Robust Error Handling** | Graceful handling of empty data (wrong ticker/date) with clear error messages and `st.stop()`. Parameter validation prevents invalid configurations. |
| NF9 | **No Look-Ahead Bias** | Position is shifted by 1 day — critical correctness requirement for reliable backtesting. |
| NF10 | **Defensive Copies** | All functions operate on `df.copy()` to prevent accidental mutation of shared state across strategies. |
| NF11 | **MultiIndex Handling** | Automatically flattens pandas MultiIndex columns that modern yfinance versions sometimes return. |
| NF12 | **Unified Hover** | Plotly charts use `hovermode="x unified"` so single vertical line shows all series values at once. |
| NF13 | **Horizontal Legends** | All chart legends positioned below chart in horizontal layout to maximize chart area. |
| NF14 | **Transparent Backgrounds** | Plotly charts use `paper_bgcolor` and `plot_bgcolor` set to `rgba(0,0,0,0)` to blend with Streamlit dark theme. |
| NF15 | **Session State Management** | Uses `st.session_state` to persist downloaded data across tab switches and widget interactions. |
| NF16 | **Loading Feedback** | Displays spinner while downloading data from Yahoo Finance to provide real-time user feedback. |
| NF17 | **Modular Architecture** | Code cleanly separated into data/ (indices), strategies/ (4 strategies), and engine/ (backtest, metrics) modules. |
| NF18 | **Reusable Indicators** | Technical indicators (RSI, SMA) implemented once in `indicators.py` and imported by all strategy functions. |
| NF19 | **Clean Dependencies** | Only 7 pip packages with pinned minimum versions. No bloated frameworks. Lightweight and maintainable. |
| NF20 | **Cross-Market Support** | Works with any Yahoo Finance ticker: US stocks, Indian stocks (.NS/.BO), ETFs, crypto, indices worldwide. |
| NF21 | **Index Constituent Lists** | Predefined lists for Nifty 50, Sensex 30, S&P 500, Nasdaq 100, Dow Jones in `data/index_constituents.py`. |
| NF22 | **Accessibility** | Text-based metrics and tables accompany every chart so information is not exclusively visual. |
| NF23 | **Transaction Cost Realism** | Costs applied only on position-change days, not every day, for realistic modeling of entry/exit fees. |

---

## 9. Supported Markets & Indices

The application provides pre-configured lists of constituents for 5 major global indices, making it easy to backtest strategies across different markets without manually entering tickers.

### India (NSE - National Stock Exchange)

**Nifty 50** — Top 50 blue-chip companies listed on NSE
- Examples: RELIANCE.NS, INFY.NS, TCS.NS, HDFC Bank, ICICI Bank, Kotak Bank, Bajaj Finance
- Total companies: 50
- Access via dropdown in app or directly use `.NS` suffix (e.g., `WIPRO.NS`)

**BSE Sensex 30** — 30 largest companies on Bombay Stock Exchange
- Mostly overlaps with Nifty 50
- Includes same major sectors: Banking, IT, Auto, Pharma, Oil & Gas, Energy
- Access via dropdown in app

### United States (NASDAQ / NYSE)

**S&P 500** — 500 largest US-listed companies
- Examples: AAPL, MSFT, GOOG, AMZN, TSLA, NVDA, META, BRK.B
- Market cap weighted index
- Access via dropdown or use bare ticker (no suffix, e.g., `AAPL`)

**Nasdaq 100** — 100 non-financial companies on Nasdaq
- Heavy tech/growth focus: AAPL, MSFT, TSLA, NVDA, ASML, AVGO
- Access via dropdown

**Dow Jones Industrial Average (DJIA)** — 30 large-cap US industrials
- Classic blue-chip index: AAPL, MSFT, JPM, JNJ, V, PG, WMT
- Access via dropdown

### Custom Ticker Entry

Not restricted to presets — users can enter **any Yahoo Finance ticker symbol** directly in the sidebar:

| Market | Example | How to Find |
|--------|---------|------------|
| **US Stocks** | AAPL, TSLA, NVDA | Use 4-letter symbol without suffix |
| **US Crypto** | BTC-USD, ETH-USD | Use "-USD" suffix for fiat pairs |
| **US ETFs** | SPY, QQQ, IVV, VOO | Use ETF ticker directly |
| **Indian Stocks (NSE)** | RELIANCE.NS, TCS.NS | Add `.NS` suffix |
| **Indian Stocks (BSE)** | RELIANCE.BO, TATASTEEL.BO | Add `.BO` suffix |
| **European Stocks** | ASML.AS, RIO.L | Use appropriate exchange suffix |
| **Global ETFs** | VGRO.TO (Canada), VAS.AX (Australia) | Use region-specific suffix |

For a complete list of Yahoo Finance tickers, visit: https://finance.yahoo.com

---

## 12. Advanced Features

The application includes several advanced features to handle real-world trading scenarios:

### Transaction Cost Modeling

Enable via **"Include Transaction Costs?"** toggle in sidebar:
- Specify cost as a **percentage** (e.g., 0.1% per trade)
- Costs applied **only on position-change days** (entry or exit), not every day
- Realistic simulation of broker commissions or slippage
- Impact visible in final returns comparison

**Example:** If transaction cost = 0.1% and Short MA changes from -1 (sell) to +1 (buy):
```
Day: Enter Long (+1)
Cost = |1 - (-1)| × 0.001 = 0.002 (0.2% of capital)
Strategy Return on that day = Daily Return × 1 − 0.002
```

### Multi-Strategy Comparison

Run all 4 strategies simultaneously on the same ticker/dates:
- **Single tab view** with side-by-side metric cards
- See which strategy wins on different metrics (total return, Sharpe, max drawdown, win rate)
- Understand strategy trade-offs under various market conditions

### Win Rate Analysis

New metric calculating percentage of **invested days with positive strategy returns**:
- Strategy earns its daily return only when Position == 1 (long)
- Win Rate = (# days with positive strategy return) / (# invested days) × 100
- Useful for understanding **consistency** beyond just total returns

### Trade Statistics

Summary of all entry/exit signals:
- **Number of trades** — count of position changes
- **Win rate (%)** — % of profitable invested days
- **Avg trade return (%)** — mean return on invested days
- **Largest win (%)** — maximum single-day return
- **Largest loss (%)** — minimum single-day return

### Modular Technical Indicators

Reusable indicator functions in `strategies/indicators.py`:
- **RSI (Relative Strength Index)** — momentum oscillator (0–100 scale)
  - Default period: 14 days
  - Calculate as: `rsi(close, period)`
  - Implementation: Wilder-style average gain/loss smoothing

Easily extensible to add more indicators (MACD, Bollinger Bands, Stochastic, etc.)

---

## 13. Known Limitations

| Limitation | Impact | Severity |
|------------|--------|----------|
| No transaction costs modeled (by default) | Overstates returns — enable toggle to model costs | Medium |
| No slippage modeled | Assumes perfect execution at closing price | Medium |
| No intraday execution | Signals at close are assumed to execute instantly at next open | Low |
| RSI-only strategy may over-trade | RSI choppy in ranging markets, generates false signals | Medium |
| Single timeframe (daily) | Ignores intraday trends or weekly/monthly patterns | Low |
| Survivorship bias | Only tests on tickers available on Yahoo Finance | Medium |
| No short selling | Strategy goes flat (cash) on sell signals rather than shorting | Low |
| No stop-loss / position sizing | No downside protection beyond the strategy's exit signal | High |
| No money management rules | Trades same position size regardless of volatility | Medium |
| Past performance caveat | Historical results do not predict future performance | High |
| Internet required | Cannot run offline — needs Yahoo Finance API | Low |
| Regime detection absent | Strategy doesn't adapt to trending vs mean-reverting markets | Medium |
| No multi-asset correlation | Single-stock testing, no portfolio diversification effects | Medium |

---

## 14. Future Enhancements & Roadmap

### Near-Term (Easy to Add)

| Feature | Description |
|---------|-------------|
| **EMA / WMA Toggle** | Add dropdown to switch between Simple, Exponential, and Weighted moving averages. EMA reacts faster to recent prices, reducing signal lag. |
| **CSV / Excel Export** | Add download buttons for backtest DataFrame, metrics table, and signal list. |
| **Dark / Light Theme Toggle** | Let users switch between dark and light modes via sidebar toggle. |
| **Email Alerts on Signals** | Generate real-time email notifications when buy/sell signals occur (integration with Gmail/AWS SES). |
| **Parameter Sensitivity Heatmap** | Test grid of (short_MA, long_MA) combinations and display heatmap of Sharpe Ratios / returns. |
| **Candlestick Charts** | Replace line chart with OHLC candlesticks for richer price action visualization. |
| **Volume Overlay** | Add secondary y-axis with volume bars to price chart. Volume spikes often confirm signal validity. |

### Mid-Term (Moderate Complexity)

| Feature | Description |
|---------|-------------|
| **Trailing Stop-Loss** | Automatically exit if price drops X% from peak since entry. Protects against catastrophic drawdowns. |
| **Dynamic Position Sizing** | Instead of binary all-in/all-out, allocate capital based on Kelly Criterion or inverse-volatility weighting. |
| **Walk-Forward Optimization** | Split into rolling in-sample/out-of-sample windows. Optimize MA on in-sample, validate on out-of-sample to detect overfitting. |
| **MACD & Bollinger Bands** | Add new technical indicators and strategies that combine them with MA signals. |
| **Regime Detection Overlay** | Use Hidden Markov Model to detect trending vs mean-reverting regimes. Only trade crossovers in trending regimes. |
| **Multi-Ticker Portfolio** | Run strategy on a basket (e.g., top 10 from Nifty 50) with portfolio-level metrics. |

### Long-Term (Advanced / Research-Grade)

| Feature | Description |
|---------|-------------|
| **Machine Learning Signal Filter** | Train classifier (Random Forest, XGBoost) on RSI, MACD, volume to predict which crossover signals are profitable. |
| **Monte Carlo Simulation** | Generate 1,000s of randomized return paths to estimate confidence intervals around Sharpe Ratio. |
| **Real-Time Streaming** | Connect Yahoo Finance WebSocket or broker API to stream live prices and generate real-time alerts. |
| **Paper Trading Integration** | Connect to Alpaca or Interactive Brokers to execute strategy in paper trading with real market conditions. |
| **Sector Rotation** | Instead of single stock, rotate capital between sectors based on strongest crossover signal. |
| **Options Overlay** | Use options (calls on buy, puts on sell) instead of stock for leveraged exposure with defined risk. |
| **User Authentication** | Add login so users can save favorite configurations and retrieve past backtest results. |

---

## 15. Tech Stack

| Layer | Technology | Role |
|-------|------------|------|
| **Frontend** | Streamlit 1.54+ | Web application framework, widgets, layout, caching |
| **Charting** | Plotly 6.5+ | Interactive charts with zoom, pan, hover, unified mode |
| **Data Source** | yfinance 0.2.31+ | Yahoo Finance historical OHLCV data API |
| **Data Processing** | pandas 2.0+, numpy 1.24+ | DataFrames, rolling windows, vectorized math |
| **Technical Indicators** | numpy, pandas | RSI, SMA calculations using rolling averages |
| **Static Charts** | matplotlib 3.7+ | Used in notebook and CLI script only |
| **Notebook** | Jupyter 1.0+ | Interactive notebook environment for reports |
| **Language** | Python 3.10+ | Core runtime (tested on 3.12) |
| **Styling** | Custom CSS + Google Fonts | Dark theme, metric cards, Outfit + JetBrains Mono fonts |

### Dependencies (Pinned Versions)

```
streamlit>=1.30.0
plotly>=5.18.0
yfinance>=0.2.31
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
jupyter>=1.0.0
```

---

## 16. Key Functions Reference

### Core Strategy Functions (`strategies/core.py`)

#### `moving_average_crossover(df, short_window, long_window) -> DataFrame`

**Purpose:** Executes classic MA Crossover strategy
- **Inputs:** DataFrame with Close prices, short MA window (default 50), long MA window (default 200)
- **Logic:** 
  - Computes SMA_Short and SMA_Long
  - Signal = +1 when SMA_Short > SMA_Long, -1 when below, 0 when equal
  - Detects crossovers: +2 = Golden Cross (buy), -2 = Death Cross (sell)
- **Output:** DataFrame with columns: Close, SMA_Short, SMA_Long, Signal, Crossover, Position, Buy_Signal, Sell_Signal
- **Key Feature:** Position shifted by 1 day to prevent look-ahead bias

#### `moving_average_rsi(df, short_window, long_window, rsi_period=14) -> DataFrame`

**Purpose:** MA Crossover with RSI confirmation filter
- **Inputs:** DataFrame, MA windows, RSI period (default 14)
- **Logic:**
  - Computes SMA_Short, SMA_Long, RSI
  - Buy when SMA_Short > SMA_Long **AND** RSI > 50
  - Sell when SMA_Short < SMA_Long **AND** RSI < 50
  - Reduces false signals in choppy markets
- **Output:** Same as MA Crossover plus RSI column
- **Use Case:** Momentum confirmation filtering

#### `rsi_only(df, rsi_period=14) -> DataFrame`

**Purpose:** Mean-reversion strategy based on RSI extremes
- **Inputs:** DataFrame, RSI period (default 14)
- **Logic:**
  - Buy when RSI < 30 (oversold)
  - Sell when RSI > 70 (overbought)
- **Output:** DataFrame with RSI, Signal, Position, Buy_Signal, Sell_Signal
- **Use Case:** Oscillator-based trading in ranging markets

#### `buy_and_hold(df) -> DataFrame`

**Purpose:** Benchmark strategy
- **Logic:** Always Position = 1 (fully invested)
- **Output:** DataFrame with constant Position = 1, no crossover signals
- **Use Case:** Passive baseline for comparison

#### `apply_strategy(df, strategy_type, params) -> DataFrame`

**Purpose:** Router function for all strategies
- **Inputs:** DataFrame, strategy name from STRATEGIES registry, parameter dict
- **Returns:** Appropriate strategy output based on selection
- **Example:** `apply_strategy(df, "MA + RSI", {"short_window": 50, "long_window": 200, "rsi_period": 14})`

### Technical Indicators (`strategies/indicators.py`)

#### `rsi(close, period=14) -> pd.Series`

**Purpose:** Calculate Relative Strength Index
- **Formula:** RSI = 100 - (100 / (1 + RS)), where RS = avg_gain / avg_loss
- **Implementation:** Wilder-style rolling average smoothing (industry standard)
- **Inputs:** Close prices series, period (default 14 days)
- **Output:** RSI series (0–100 scale)
- **Interpretation:**
  - RSI < 30: Oversold condition
  - RSI > 70: Overbought condition
  - RSI 30–70: Neutral zone

### Backtesting Engine (`engine/backtest.py`)

#### `backtest_strategy(df, initial_capital, transaction_cost_pct=0.0, use_transaction_cost=False) -> DataFrame`

**Purpose:** Simulate portfolio performance
- **Logic:**
  - Strategy Return = Daily Return × (Position == 1)
  - BuyHold Return = Daily Return (always long)
  - If transaction costs enabled: subtract cost on position-change days
- **Inputs:**
  - DataFrame with Close, Position columns
  - initial_capital (e.g., $100,000)
  - transaction_cost_pct (e.g., 0.1 for 0.1%)
- **Output:** DataFrame with Strategy_Return, BuyHold_Return, Strategy_Value, BuyHold_Value
- **Key Feature:** Applies costs only when position changes (entry/exit), not every day

### Performance Metrics (`engine/metrics.py`)

#### `calculate_metrics(returns, label="Strategy") -> dict`

**Purpose:** Compute 5 institutional-grade performance metrics
- **Returns dict with:**
  - **Total Return:** `(1 + r).prod() - 1`
  - **Annualized Return:** `(1 + total)^(1/years) - 1`
  - **Annualized Volatility:** `std(r) × sqrt(252)`
  - **Sharpe Ratio:** `annualized_return / annualized_volatility` (risk-free rate = 0)
  - **Max Drawdown:** `min((cum - cum.cummax()) / cum.cummax())`
- **Inputs:** Daily return series, label (for reporting)

#### `get_win_rate(backtest_df) -> float`

**Purpose:** Calculate percentage of invested days with positive returns
- **Logic:** `(# days with positive strategy return) / (# invested days) × 100`
- **Significance:** Measures consistency/reliability of strategy

#### `generate_trade_summary(df_strat, backtest_df) -> dict`

**Purpose:** Summarize all trades
- **Returns dict with:**
  - `num_trades`: Count of position changes
  - `win_rate`: % of profitable invested days
  - `avg_trade_return_pct`: Mean return on invested days
  - `largest_win_pct`: Maximum single-day gain
  - `largest_loss_pct`: Maximum single-day loss

### Data & Index Constituents (`data/index_constituents.py`)

#### `get_index_options() -> dict`

**Purpose:** Provide dropdown menu of index constituents
- **Returns:** Dictionary mapping "Nifty 50" → [(ticker, name), ...], etc.
- **Indices Included:**
  - Nifty 50 (NSE, 50 companies)
  - BSE Sensex 30 (NSE symbols, 30 companies)
  - S&P 500 (500 US companies)
  - Nasdaq 100 (100 US tech/growth)
  - Dow Jones (30 US industrials)
- **Usage:** Streamlit selectbox widget population

---

## 17. Module Reference

### Module Structure

```
P1/
├── data/index_constituents.py       # Global index definitions
├── strategies/core.py               # 4 strategy implementations + router
├── strategies/indicators.py         # Technical indicators (RSI, SMA)
├── engine/backtest.py              # Backtesting engine with costs
└── engine/metrics.py               # Metrics: Sharpe, drawdown, win rate, trades
```

### How Modules Interact

```
User Input (Streamlit UI)
    ↓
app.py calls: get_index_options() to populate dropdown
    ↓
User selects ticker & strategy
    ↓
app.py calls: download_data(ticker) → [yfinance]
    ↓
app.py calls: apply_strategy(df, strategy, params) → [strategies/core.py]
    ↓
strategies/core.py calls: indicators.rsi() or uses SMA
    ↓
app.py calls: backtest_strategy(df, capital, costs) → [engine/backtest.py]
    ↓
app.py calls: calculate_metrics() & generate_trade_summary() → [engine/metrics.py]
    ↓
Render charts & metrics in Streamlit tabs
```

### Extending the System

**To add a new strategy:**
1. Implement function in `strategies/core.py` following same signature: `def my_strategy(df, **params) -> DataFrame`
2. Return DataFrame with `Signal`, `Position`, `Buy_Signal`, `Sell_Signal` columns
3. Add to `STRATEGIES` dict in `core.py`
4. Now selectable in app.py dropdown without any UI changes

**To add new indicators:**
1. Implement function in `strategies/indicators.py` (e.g., `def macd(close) -> tuple`)
2. Import and call from strategy functions
3. Non-invasive — doesn't require UI changes

---

## 18. License & Disclaimer

This project is provided for **educational and research purposes only**. It is **not financial advice**. Do not use this tool to make real investment decisions without consulting a qualified financial advisor.

- Historical backtest results **do not guarantee future performance**.
- The strategy does not account for transaction costs, slippage, taxes, or market impact.
- The author assumes no liability for financial losses incurred from using this tool.

---

*Built with Streamlit, Plotly, and yfinance. Data sourced from Yahoo Finance.*
