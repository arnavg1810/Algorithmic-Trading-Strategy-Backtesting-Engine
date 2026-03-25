"""
Multi-Strategy Quantitative Trading Dashboard
Modular backtesting: MA Crossover, MA+RSI, RSI Only, Buy & Hold.
Built with Streamlit & Plotly. Supports Nifty 50, BSE Sensex, S&P 500, Nasdaq 100, Dow Jones.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.index_constituents import get_index_options
from strategies.core import apply_strategy, STRATEGIES
from engine.backtest import backtest_strategy
from engine.metrics import calculate_metrics, get_win_rate, generate_trade_summary

TRADING_DAYS_PER_YEAR = 252

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MA Crossover Strategy",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Distinctive palette: deep navy + cyan/amber accent
COLORS = {
    "bg": "#0a0e14",
    "surface": "#111820",
    "card": "#151c26",
    "accent": "#e6a23c",
    "accent_dim": "#b8860b",
    "cyan": "#4fc3f7",
    "cyan_dim": "#42a5f5",
    "green": "#52c41a",
    "red": "#f5222d",
    "orange": "#fa8c16",
    "blue": "#1890ff",
    "text": "#e8e6e3",
    "muted": "#8b949e",
    "border": "#2d3748",
}

# Elevated UI: premium hierarchy, metrics with icons/glow, sidebar summary, tabs, footer
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
    :root {
        --font-display: 'Outfit', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
        --accent: #e6a23c;
        --accent-dim: #b8860b;
        --cyan: #4fc3f7;
        --cyan-dim: #42a5f5;
        --surface: #111820;
        --card: #151c26;
        --border: #2d3748;
        --text: #e8e6e3;
        --muted: #8b949e;
        --green: #52c41a;
        --red: #f5222d;
    }
    .stApp {
        background: linear-gradient(160deg, #0a0e14 0%, #0d1219 50%, #111820 100%);
        transition: background 0.4s ease;
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
    }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    .section-header { font-family: var(--font-display) !important; font-size: 1.5rem !important; font-weight: 600 !important; letter-spacing: -0.02em !important; margin-bottom: 1rem !important; color: var(--text) !important; }
    .section-body { color: var(--muted) !important; font-weight: 400 !important; line-height: 1.6 !important; }
    .metric-card {
        background: linear-gradient(145deg, var(--card) 0%, #1a2230 100%);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        font-family: var(--font-display);
        position: relative;
        overflow: hidden;
    }
    .metric-card::after {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--accent), var(--accent-dim));
        opacity: 0;
        transition: opacity 0.25s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    }
    .metric-card.metric-glow-green:hover { box-shadow: 0 8px 28px rgba(82, 196, 26, 0.2); }
    .metric-card.metric-glow-red:hover { box-shadow: 0 8px 28px rgba(245, 34, 45, 0.2); }
    .metric-card:hover::after { opacity: 1; }
    .metric-icon { font-size: 1.1rem; margin-bottom: 4px; opacity: 0.9; }
    .metric-label {
        font-size: 0.7rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 4px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    .metric-delta { font-size: 0.8rem; font-weight: 600; margin-top: 2px; }
    .metric-green .metric-value { color: var(--green); }
    .metric-red .metric-value { color: var(--red); }
    .metric-green .metric-delta { color: var(--green); }
    .metric-red .metric-delta { color: var(--red); }
    .section-divider { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e14 0%, #0f1419 100%);
        border-right: 1px solid var(--border);
    }
    .sidebar-summary {
        background: linear-gradient(145deg, #151c26 0%, #1a2230 100%);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        font-family: var(--font-display);
    }
    .sidebar-summary .summary-row { font-size: 0.85rem; margin-bottom: 8px; display: flex; justify-content: space-between; }
    .sidebar-summary .summary-label { color: var(--muted); }
    .sidebar-summary .summary-val { color: var(--text); font-weight: 600; }
    .sidebar-card {
        background: rgba(21, 28, 38, 0.8);
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 14px;
        border: 1px solid var(--border);
    }
    .regime-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .regime-bullish { background: rgba(82, 196, 26, 0.25); color: #52c41a; }
    .regime-bearish { background: rgba(245, 34, 45, 0.25); color: #f5222d; }
    .regime-neutral { background: rgba(250, 173, 20, 0.25); color: #faad14; }
    div[data-testid="stSidebar"] .stMarkdown { font-family: var(--font-display); }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; margin-bottom: 1rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 12px 20px;
        font-family: var(--font-display);
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:first-child { margin-left: 0; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #1f2937, #111827) !important;
        border-bottom: 2px solid var(--cyan) !important;
    }
    .hero-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 20px;
        padding: 12px 0 28px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 16px;
    }
    .hero-title {
        font-family: var(--font-display) !important;
        font-weight: 800 !important;
        font-size: 48px !important;
        letter-spacing: -0.03em !important;
        line-height: 1.1 !important;
        margin: 0 0 8px 0 !important;
        background: linear-gradient(90deg, #4fc3f7, #42a5f5) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    .hero-subtitle {
        color: var(--muted) !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        margin: 0 !important;
    }
    .hero-badges { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dim) 100%);
        color: #0a0e14 !important;
        padding: 8px 16px;
        border-radius: 999px;
        font-family: var(--font-mono);
        font-size: 0.95rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        box-shadow: 0 0 20px rgba(230, 162, 60, 0.4);
    }
    .hero-ma { color: var(--muted); font-size: 0.9rem; }
    .footer-bar {
        text-align: center;
        padding: 24px 16px;
        margin-top: 32px;
        border-top: 1px solid var(--border);
        color: var(--muted);
        font-size: 0.85rem;
    }
    .footer-bar a { color: var(--cyan); text-decoration: none; }
    [data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 12px;
    }
    .tab-content { animation: fadeIn 0.4s ease; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────

# Icons for metrics (emoji)
METRIC_ICONS = {
    "Total Return": "📈",
    "Annualized Return": "📊",
    "Annualized Volatility": "📉",
    "Sharpe Ratio": "⚖",
    "Max Drawdown": "📉",
    "Final Value": "💰",
    "Win Rate": "🎯",
}


def metric_card(label, value, css_class=""):
    return f"""
    <div class="metric-card {css_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """


def metric_card_advanced(icon: str, label: str, value: str, delta: str = "", glow_class: str = ""):
    delta_html = f'<div class="metric-delta {glow_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card {glow_class}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """


def get_regime(df_strat: pd.DataFrame) -> str:
    """Bullish if short MA > long MA (last valid); only for strategies with SMA columns."""
    if "SMA_Short" not in df_strat.columns or "SMA_Long" not in df_strat.columns:
        return "—"
    valid = df_strat.dropna(subset=["SMA_Short", "SMA_Long"])
    if valid.empty:
        return "Neutral"
    last = valid.iloc[-1]
    if last["SMA_Short"] > last["SMA_Long"]:
        return "Bullish"
    if last["SMA_Short"] < last["SMA_Long"]:
        return "Bearish"
    return "Neutral"


@st.cache_data(show_spinner=False)
def download_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download OHLC and return Close-only dataframe. Cached by (ticker, start, end)."""
    raw = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame()
    df = raw[["Close"]].copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    df.dropna(inplace=True)
    return df


@st.cache_data(show_spinner=False)
def cached_strategy_and_backtest(
    ticker: str,
    start: str,
    end: str,
    strategy_type: str,
    short_w: int,
    long_w: int,
    rsi_period: int,
    initial_capital: float,
    use_transaction_cost: bool,
    transaction_cost_pct: float,
) -> tuple:
    """
    Returns (df_strat, backtest_df) for given params. Cached to avoid recalc when params unchanged.
    """
    raw = download_data(ticker, start, end)
    if raw.empty:
        return pd.DataFrame(), pd.DataFrame()
    params = {"short_window": short_w, "long_window": long_w, "rsi_period": rsi_period}
    df_strat = apply_strategy(raw, strategy_type, params)
    backtest_df = backtest_strategy(
        df_strat,
        initial_capital,
        transaction_cost_pct=transaction_cost_pct,
        use_transaction_cost=use_transaction_cost,
    )
    return df_strat, backtest_df


# ──────────────────────────────────────────────────────────────
# SIDEBAR — USER CONTROLS
# ──────────────────────────────────────────────────────────────
index_options = get_index_options()
index_ids = list(index_options.keys())
index_labels = [index_options[k][0] for k in index_ids]

with st.sidebar:
    st.markdown("## Configuration")
    # Strategy summary (regime/ticker/index filled after run)
    last_regime = st.session_state.get("last_regime", "—")
    last_index = st.session_state.get("last_index_label", index_labels[2])
    last_ticker = st.session_state.get("last_ticker", "—")
    regime_class = "regime-bullish" if last_regime == "Bullish" else ("regime-bearish" if last_regime == "Bearish" else "regime-neutral")
    st.markdown(
        f"""
    <div class="sidebar-summary">
        <div class="summary-row"><span class="summary-label">Strategy</span><span class="summary-val">{st.session_state.get("last_strategy_label", "—")}</span></div>
        <div class="summary-row"><span class="summary-label">Ticker</span><span class="summary-val">{last_ticker}</span></div>
        <div class="summary-row"><span class="summary-label">Market</span><span class="summary-val">{last_index}</span></div>
        <div class="summary-row"><span class="summary-label">Regime</span><span class="regime-chip {regime_class}">{last_regime}</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("#### Market & Stock")

    index_choice = st.selectbox(
        "Index / Market",
        options=range(len(index_ids)),
        format_func=lambda i: index_labels[i],
        index=2,
    )
    index_id = index_ids[index_choice]
    _, constituents = index_options[index_id]
    # Build options: "SYMBOL — Name"
    stock_options = [f"{s[0]} — {s[1]}" for s in constituents]
    stock_choice = st.selectbox(
        "Select Stock",
        options=range(len(stock_options)),
        format_func=lambda i: stock_options[i],
        index=0,
    )
    ticker = constituents[stock_choice][0]

    st.markdown("---")
    st.markdown("#### Custom Ticker (optional)")
    custom = st.text_input("Or enter any Yahoo Finance ticker", value="", placeholder="e.g. MSFT, RELIANCE.NS")
    if custom and custom.strip():
        ticker = custom.strip().upper()

    st.markdown("---")
    st.markdown("#### Date Range")
    today = datetime.today().date()
    default_start = today - timedelta(days=5 * 365)
    col_s, col_e = st.columns(2)
    with col_s:
        start_date = st.date_input("Start", value=default_start, max_value=today)
    with col_e:
        end_date = st.date_input("End", value=today, max_value=today)

    st.markdown("---")
    st.markdown("#### Strategy")
    strategy_options = list(STRATEGIES.keys())
    strategy_choice = st.selectbox(
        "Strategy Type",
        options=strategy_options,
        index=0,
        key="strategy_type",
    )
    # Conditional parameters
    short_window, long_window, rsi_period = 50, 200, 14
    if strategy_choice in ("Moving Average Crossover", "MA + RSI"):
        short_window = st.slider("Short MA Window (days)", 5, 100, 50, step=5, key="sw")
        long_window = st.slider("Long MA Window (days)", 50, 400, 200, step=10, key="lw")
        if short_window >= long_window:
            st.error("Short MA must be less than Long MA.")
            st.stop()
    if strategy_choice in ("MA + RSI", "RSI Only"):
        rsi_period = st.slider("RSI Period", 5, 30, 14, step=1, key="rsi_p")

    st.markdown("---")
    st.markdown("#### Backtest Settings")
    initial_capital = st.number_input(
        "Initial Capital ($)", min_value=1_000, max_value=10_000_000, value=100_000, step=10_000
    )
    use_transaction_cost = st.checkbox("Apply transaction cost", value=False, key="use_tc")
    transaction_cost_pct = 0.0
    if use_transaction_cost:
        transaction_cost_pct = st.number_input(
            "Transaction Cost (% per trade)", min_value=0.01, max_value=2.0, value=0.1, step=0.05, format="%.2f", key="tc_pct"
        )

    run_btn = st.button("Run Strategy", type="primary", use_container_width=True)

# ──────────────────────────────────────────────────────────────
# HEADER — Premium 48px gradient title, subtitle, ticker badge + regime
# ──────────────────────────────────────────────────────────────
_regime = st.session_state.get("last_regime", "—")
regime_chip_class = "regime-bullish" if _regime == "Bullish" else ("regime-bearish" if _regime == "Bearish" else "regime-neutral")
_ma_badge = f"{short_window} / {long_window} SMA" if strategy_choice in ("Moving Average Crossover", "MA + RSI") else strategy_choice
st.markdown(
    f"""
    <div class="hero-wrap">
        <div>
            <h1 class="hero-title">Quantitative Trading Dashboard</h1>
            <p class="hero-subtitle">Multi-strategy backtest · Nifty 50 · Sensex · S&P 500 · Nasdaq · Dow Jones</p>
        </div>
        <div class="hero-badges">
            <span class="hero-badge">{ticker}</span>
            <span class="regime-chip {regime_chip_class}">{_regime}</span>
            <span class="hero-ma">{_ma_badge}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# TABS — 7 sections (Overview, Strategy, Data Analysis, Performance, Insights, Optimize, About)
# ──────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Overview",
    "Strategy",
    "📊 Data Analysis",
    "Performance",
    "Insights",
    "Optimize",
    "About",
])

# Load data and run strategy (cached when params unchanged)
if "df_raw" not in st.session_state or run_btn:
    with st.spinner(f"Downloading {ticker} data..."):
        raw = download_data(ticker, str(start_date), str(end_date))
    if raw.empty:
        st.error(f"No data returned for **{ticker}**. Check the ticker symbol and date range.")
        st.stop()
    st.session_state["df_raw"] = raw

df_strat, backtest = cached_strategy_and_backtest(
    ticker,
    str(start_date),
    str(end_date),
    strategy_choice,
    short_window,
    long_window,
    rsi_period,
    initial_capital,
    use_transaction_cost,
    transaction_cost_pct,
)
if backtest.empty:
    st.error("Backtest produced no data. Check date range and parameters.")
    st.stop()

raw = st.session_state["df_raw"]
strat_m = calculate_metrics(backtest["Strategy_Return"], strategy_choice)
bh_m = calculate_metrics(backtest["BuyHold_Return"], "Buy & Hold")
regime = get_regime(df_strat)
win_rate = get_win_rate(backtest)
trade_summary = generate_trade_summary(df_strat, backtest)

st.session_state["last_regime"] = regime
st.session_state["last_ticker"] = ticker
st.session_state["last_index_label"] = index_labels[index_choice]
st.session_state["last_strategy_label"] = strategy_choice

buy_dates = df_strat[df_strat["Buy_Signal"]].index if "Buy_Signal" in df_strat.columns else pd.DatetimeIndex([])
sell_dates = df_strat[df_strat["Sell_Signal"]].index if "Sell_Signal" in df_strat.columns else pd.DatetimeIndex([])
_cum = (1 + backtest["Strategy_Return"]).cumprod()
_drawdown = (_cum - _cum.cummax()) / _cum.cummax()

# ──────────────────── TAB 0 : OVERVIEW (Dashboard) ────────────────────
final_val = backtest["Strategy_Value"].iloc[-1]
strat_vs_bh = (strat_m["Total Return"] - bh_m["Total Return"]) * 100
with tabs[0]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    # Metrics row: big numbers, icons, deltas, glow
    st.markdown("### Key metrics")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        delta_tr = f"▲ +{strat_vs_bh:.1f}% vs B&H" if strat_vs_bh >= 0 else f"▼ {strat_vs_bh:.1f}% vs B&H"
        gl = "metric-glow-green" if strat_m["Total Return"] >= 0 else "metric-glow-red"
        cl = "metric-green" if strat_m["Total Return"] >= 0 else "metric-red"
        st.markdown(metric_card_advanced("📈", "Total Return", f"{strat_m['Total Return']*100:+.2f}%", delta_tr, f"{cl} {gl}"), unsafe_allow_html=True)
    with c2:
        sh_glow = "metric-glow-green" if strat_m["Sharpe Ratio"] > 0 else ""
        st.markdown(metric_card_advanced("⚖", "Sharpe Ratio", f"{strat_m['Sharpe Ratio']:.3f}", "", sh_glow), unsafe_allow_html=True)
    with c3:
        dd_glow = "metric-glow-red"
        st.markdown(metric_card_advanced("📉", "Max Drawdown", f"{strat_m['Max Drawdown']*100:.2f}%", "", "metric-red " + dd_glow), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card_advanced("🎯", "Win Rate", f"{win_rate:.1f}%", "", ""), unsafe_allow_html=True)
    with c5:
        st.markdown(metric_card_advanced("💰", "Final Value", f"${final_val:,.0f}", "", "metric-glow-green" if final_val >= initial_capital else "metric-glow-red"), unsafe_allow_html=True)

    # TradingView-style layout: [Price + Signals | Risk Summary]
    st.markdown("---")
    col_chart, col_risk = st.columns([2, 1])
    with col_chart:
        st.markdown("#### Price & signals")
        valid = df_strat.dropna(subset=["Close"])
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=valid.index, y=valid["Close"], name="Close", line=dict(color="#b0bec5", width=1.5), opacity=0.95))
        if "SMA_Short" in df_strat.columns and "SMA_Long" in df_strat.columns:
            v_ma = df_strat.dropna(subset=["SMA_Short", "SMA_Long"])
            fig1.add_trace(go.Scatter(x=v_ma.index, y=v_ma["SMA_Short"], name=f"{short_window}-day SMA", line=dict(color=COLORS["blue"], width=2.5)))
            fig1.add_trace(go.Scatter(x=v_ma.index, y=v_ma["SMA_Long"], name=f"{long_window}-day SMA", line=dict(color=COLORS["orange"], width=2.5)))
        if "Buy_Signal" in df_strat.columns and df_strat["Buy_Signal"].any():
            buys = df_strat[df_strat["Buy_Signal"]]
            fig1.add_trace(go.Scatter(x=buys.index, y=buys["Close"], mode="markers", name="Buy", marker=dict(symbol="triangle-up", size=14, color=COLORS["green"], line=dict(width=1, color="white"))))
        if "Sell_Signal" in df_strat.columns and df_strat["Sell_Signal"].any():
            sells = df_strat[df_strat["Sell_Signal"]]
            fig1.add_trace(go.Scatter(x=sells.index, y=sells["Close"], mode="markers", name="Sell", marker=dict(symbol="triangle-down", size=14, color=COLORS["red"], line=dict(width=1, color="white"))))
        fig1.update_layout(template="plotly_dark", height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=50, r=30, t=40, b=50), hovermode="x unified", showlegend=True, legend=dict(orientation="h", y=1.02))
        st.plotly_chart(fig1, use_container_width=True)
    with col_risk:
        st.markdown("#### Risk summary")
        st.markdown(f"**Max drawdown:** {_drawdown.min()*100:.2f}%")
        st.markdown(f"**Ann. volatility:** {strat_m['Annualized Volatility']*100:.2f}%")
        st.markdown(f"**Ann. return:** {strat_m['Annualized Return']*100:+.2f}%")
        st.markdown(f"**Trades (buy):** {len(buy_dates)}")
        st.markdown(f"**Trades (sell):** {len(sell_dates)}")

    # Row 2: [Equity curve | Drawdown]
    col_equity, col_dd = st.columns([2, 1])
    with col_equity:
        st.markdown("#### Equity curve")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=backtest.index, y=backtest["Strategy_Value"], name="Strategy", line=dict(color=COLORS["blue"], width=2.5), fill="tozeroy", fillcolor="rgba(24, 144, 255, 0.15)"))
        fig2.add_trace(go.Scatter(x=backtest.index, y=backtest["BuyHold_Value"], name="Buy & Hold", line=dict(color=COLORS["orange"], width=2.5)))
        fig2.add_hline(y=initial_capital, line_dash="dash", line_color="grey")
        fig2.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=50, r=30, t=50, b=50), hovermode="x unified", legend=dict(orientation="h", y=1.06, yanchor="bottom"))
        st.plotly_chart(fig2, use_container_width=True)
    with col_dd:
        st.markdown("#### Drawdown")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=_drawdown.index, y=_drawdown * 100, name="Drawdown", line=dict(color=COLORS["red"], width=1.5), fill="tozeroy", fillcolor="rgba(245, 34, 45, 0.25)"))
        fig3.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=50, r=30, t=30, b=50), yaxis_title="%", hovermode="x unified")
        st.plotly_chart(fig3, use_container_width=True)

    # Trade log full width
    st.markdown("---")
    st.markdown("#### Trade log")
    if len(buy_dates) > 0 or len(sell_dates) > 0:
        rows = []
        for d in buy_dates:
            rows.append({"Date": d.date(), "Signal": "Buy", "Close": f"${df_strat.loc[d, 'Close']:.2f}"})
        for d in sell_dates:
            rows.append({"Date": d.date(), "Signal": "Sell", "Close": f"${df_strat.loc[d, 'Close']:.2f}"})
        trade_df = pd.DataFrame(rows).sort_values("Date")
        st.dataframe(trade_df, use_container_width=True, hide_index=True)
    else:
        st.info("No signals in this period.")
    st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────── TAB 1 : STRATEGY (Explanation + Trade Summary) ────────────────────
STRATEGY_EXPLANATIONS = {
    "Moving Average Crossover": f"""
- **Short MA ({short_window}d)** and **Long MA ({long_window}d)**: rolling mean of Close.
- **Buy** when Short MA crosses above Long MA (Golden Cross); **Sell** when Short MA crosses below Long MA (Death Cross).
- **Position** = Signal shifted by 1 day to avoid look-ahead bias (execute at t+1 open).
""",
    "MA + RSI": f"""
- **Short MA ({short_window}d)** and **Long MA ({long_window}d)** plus **RSI ({rsi_period}d)**.
- **Buy** when Short MA > Long MA **and** RSI > 50; **Sell** when Short MA < Long MA **and** RSI < 50.
- **Position** shifted by 1 day to avoid look-ahead bias.
""",
    "RSI Only": f"""
- **RSI ({rsi_period}d)**: oversold &lt; 30, overbought &gt; 70.
- **Buy** when RSI &lt; 30 (oversold); **Sell** when RSI &gt; 70 (overbought).
- **Position** shifted by 1 day to avoid look-ahead bias.
""",
    "Buy & Hold": """
- Always invested (Position = 1). No signals; benchmark strategy.
""",
}
with tabs[1]:
    st.markdown("### Strategy explanation")
    st.markdown(STRATEGY_EXPLANATIONS.get(strategy_choice, ""))
    st.markdown("---")
    st.markdown("### Trade summary")
    ts = trade_summary
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Number of trades", f"{ts['num_trades']:,}")
    c2.metric("Win rate", f"{ts['win_rate']:.1f}%")
    c3.metric("Avg trade return", f"{ts['avg_trade_return_pct']:.2f}%")
    c4.metric("Largest win", f"{ts['largest_win_pct']:.2f}%")
    c5.metric("Largest loss", f"{ts['largest_loss_pct']:.2f}%")
    st.markdown("---")
    st.markdown("### Data")
    c1, c2, c3 = st.columns(3)
    c1.metric("Trading Days", f"{len(raw):,}")
    c2.metric("Start", str(raw.index.min().date()))
    c3.metric("End", str(raw.index.max().date()))
    st.markdown("#### Summary statistics")
    st.dataframe(raw.describe().round(2), use_container_width=True)
    st.markdown("---")
    buy_col, sell_col = st.columns(2)
    with buy_col:
        st.markdown(f"#### Buy Signals ({len(buy_dates)})")
        if len(buy_dates) > 0:
            buy_df = pd.DataFrame({
                "Date": [d.date() for d in buy_dates],
                "Close Price": [f"${df_strat.loc[d, 'Close']:.2f}" for d in buy_dates],
            })
            st.dataframe(buy_df, use_container_width=True, hide_index=True)
        else:
            st.info("No buy signals in this period.")
    with sell_col:
        st.markdown(f"#### Sell Signals ({len(sell_dates)})")
        if len(sell_dates) > 0:
            sell_df = pd.DataFrame({
                "Date": [d.date() for d in sell_dates],
                "Close Price": [f"${df_strat.loc[d, 'Close']:.2f}" for d in sell_dates],
            })
            st.dataframe(sell_df, use_container_width=True, hide_index=True)
        else:
            st.info("No sell signals in this period.")

# ──────────────────── TAB 2 : DATA ANALYSIS ────────────────────
def _daily_returns_histogram(backtest_df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=backtest_df["Strategy_Return"] * 100, nbinsx=50, name="Strategy", marker_color=COLORS["blue"], opacity=0.75))
    fig.add_trace(go.Histogram(x=backtest_df["BuyHold_Return"] * 100, nbinsx=50, name="Buy & Hold", marker_color=COLORS["orange"], opacity=0.6))
    fig.update_layout(
        template="plotly_dark",
        height=380,
        title="Daily returns (%)",
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=30, t=80, b=50),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def _monthly_heatmap(backtest_df: pd.DataFrame):
    """Monthly returns heatmap with full 12-month grid alignment."""
    rets = backtest_df["Strategy_Return"].copy()
    rets.index = pd.to_datetime(rets.index)
    monthly = rets.resample("M").apply(lambda x: (1 + x).prod() - 1) * 100
    
    # Create DataFrame for pivot table
    monthly_df = pd.DataFrame({
        "Year": monthly.index.year,
        "Month": monthly.index.month,
        "Returns": monthly.values
    })
    
    # Pivot table with years as rows, months as columns
    heatmap_data = monthly_df.pivot(
        index="Year",
        columns="Month",
        values="Returns"
    )
    
    # Reindex to ensure all 12 months are present (1-12)
    heatmap_data = heatmap_data.reindex(columns=range(1, 13))
    
    # Fill NaN with 0 only for visualization
    plot_data = heatmap_data.fillna(0)
    
    # Create heatmap using px.imshow for proper grid alignment
    fig = px.imshow(
        plot_data,
        labels=dict(x="Month", y="Year", color="Return %"),
        color_continuous_scale="RdYlGn",
        aspect="auto",
        origin="upper",
        zmin=-20,
        zmax=20
    )
    
    # Fix axes configuration
    fig.update_xaxes(
        tickmode="linear",
        tick0=1,
        dtick=1,
        tickvals=list(range(12)),
        ticktext=list(range(1, 13))
    )
    
    fig.update_yaxes(autorange="reversed")
    
    fig.update_layout(
        template="plotly_dark",
        height=400,
        title="Monthly returns (%)",
        xaxis_title="Month",
        yaxis_title="Year",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=50, t=40, b=50),
        coloraxis_colorbar=dict(title="Return %")
    )
    
    return fig

def _rolling_volatility(backtest_df: pd.DataFrame, window: int = 30):
    rets = backtest_df["Strategy_Return"]
    roll_vol = rets.rolling(window=window, min_periods=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll_vol.index, y=roll_vol, name=f"Rolling {window}d vol (%)", line=dict(color=COLORS["cyan"], width=2)))
    fig.update_layout(template="plotly_dark", height=320, title=f"Rolling {window}-day volatility (ann. %)", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=50, r=30, t=40, b=50), hovermode="x unified")
    return fig

def _rolling_sharpe(backtest_df: pd.DataFrame, window: int = 30):
    rets = backtest_df["Strategy_Return"]
    roll_ret = rets.rolling(window=window, min_periods=window).mean() * TRADING_DAYS_PER_YEAR
    roll_vol = rets.rolling(window=window, min_periods=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    roll_sharpe = np.where(roll_vol != 0, roll_ret / roll_vol, np.nan)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rets.index, y=roll_sharpe, name=f"Rolling {window}d Sharpe", line=dict(color=COLORS["accent"], width=2)))
    fig.update_layout(template="plotly_dark", height=320, title=f"Rolling {window}-day Sharpe ratio", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=50, r=30, t=40, b=50), hovermode="x unified")
    return fig

with tabs[2]:
    st.markdown("### Data Analysis")
    st.markdown("Daily and monthly return distributions, rolling volatility and Sharpe, and optional benchmark correlation.")
    row1a, row1b = st.columns(2)
    with row1a:
        st.plotly_chart(_daily_returns_histogram(backtest), use_container_width=True)
    with row1b:
        st.plotly_chart(_monthly_heatmap(backtest), use_container_width=True)
    row2a, row2b = st.columns(2)
    with row2a:
        st.plotly_chart(_rolling_volatility(backtest, 30), use_container_width=True)
    with row2b:
        st.plotly_chart(_rolling_sharpe(backtest, 30), use_container_width=True)
    st.markdown("#### Optional: benchmark correlation")
    bench_ticker = st.text_input("Benchmark ticker (e.g. SPY, ^GSPC, ^NSEI)", value="", placeholder="Leave empty to skip", key="bench_ticker")
    if bench_ticker and bench_ticker.strip():
        ticker_clean = bench_ticker.strip().upper()
        with st.spinner("Loading benchmark..."):
            bench_raw = download_data(ticker_clean, str(start_date), str(end_date))
        if bench_raw.empty and not ticker_clean.startswith("^"):
            bench_raw = download_data("^" + ticker_clean, str(start_date), str(end_date))
        if not bench_raw.empty:
            bench_ret = bench_raw["Close"].pct_change()
            strat_ret = backtest["Strategy_Return"]
            common_idx = strat_ret.index.intersection(bench_ret.index)
            if len(common_idx) < 2:
                st.warning("Not enough overlapping dates between strategy and benchmark.")
            else:
                s = strat_ret.reindex(common_idx).fillna(0)
                b = bench_ret.reindex(common_idx).fillna(0)
                corr = s.corr(b)
                st.metric("Correlation with benchmark", f"{corr:.3f}")
                st.caption(f"Computed over {len(common_idx)} overlapping trading days.")
        else:
            st.warning("No benchmark data found. Try with ^ prefix for indices (e.g. ^NSEI, ^GSPC).")

# ──────────────────── TAB 3 : PERFORMANCE ─────────────────────
with tabs[3]:
    st.markdown("### Backtest assumptions")
    tc_note = f"Transaction cost **{transaction_cost_pct}%** per trade applied." if use_transaction_cost else "No transaction costs."
    st.markdown(f"Initial capital **${initial_capital:,.0f}** · Fully invested when long · {tc_note} · No slippage.")
    st.markdown("---")
    st.markdown("### Strategy vs Buy & Hold")
    labels = ["Total Return", "Annualized Return", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown"]
    fmt = [
        lambda v: f"{v*100:+.2f}%",
        lambda v: f"{v*100:+.2f}%",
        lambda v: f"{v*100:.2f}%",
        lambda v: f"{v:.3f}",
        lambda v: f"{v*100:.2f}%",
    ]
    cols = st.columns(5)
    for i, (lab, fn) in enumerate(zip(labels, fmt)):
        with cols[i]:
            sv = fn(strat_m[lab])
            css = "metric-green" if (strat_m[lab] >= bh_m[lab] and "Drawdown" not in lab) else ("metric-green" if "Drawdown" in lab and strat_m[lab] > bh_m[lab] else "metric-red")
            icon = METRIC_ICONS.get(lab, "📊")
            delta = f"▲ vs B&H" if (lab != "Max Drawdown" and strat_m[lab] >= bh_m[lab]) or (lab == "Max Drawdown" and strat_m[lab] > bh_m[lab]) else ""
            st.markdown(metric_card_advanced(icon, f"Strategy {lab}", sv, delta, css), unsafe_allow_html=True)
    cols2 = st.columns(5)
    for i, (lab, fn) in enumerate(zip(labels, fmt)):
        with cols2[i]:
            st.markdown(metric_card_advanced(METRIC_ICONS.get(lab, "📊"), f"Buy & Hold {lab}", fn(bh_m[lab]), "", ""), unsafe_allow_html=True)
    st.markdown("#### Daily returns distribution")
    fig_dist = make_subplots(rows=1, cols=2, subplot_titles=("Strategy", "Buy & Hold"))
    fig_dist.add_trace(go.Histogram(x=backtest["Strategy_Return"], nbinsx=80, marker_color=COLORS["blue"], opacity=0.75), row=1, col=1)
    fig_dist.add_trace(go.Histogram(x=backtest["BuyHold_Return"], nbinsx=80, marker_color=COLORS["orange"], opacity=0.75), row=1, col=2)
    fig_dist.update_layout(template="plotly_dark", height=320, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig_dist, use_container_width=True)
    st.markdown("### Understanding the metrics")
    with st.expander("Total Return", expanded=False):
        st.markdown("Raw percentage gain or loss over the period.")
    with st.expander("Annualized Return", expanded=False):
        st.markdown("Per-year equivalent return for comparison across horizons.")
    with st.expander("Annualized Volatility", expanded=False):
        st.markdown("Annualized standard deviation of daily returns.")
    with st.expander("Sharpe Ratio", expanded=False):
        st.markdown("Risk-adjusted return. >1 good, >2 excellent.")
    with st.expander("Maximum Drawdown", expanded=False):
        st.markdown("Largest peak-to-trough decline.")

# ──────────────────── TAB 4 : INSIGHTS ────────────────────────
with tabs[4]:
    st.markdown("### Key Insights")

    outperforms = strat_m["Total Return"] > bh_m["Total Return"]
    sharpe_better = strat_m["Sharpe Ratio"] > bh_m["Sharpe Ratio"]
    dd_better = strat_m["Max Drawdown"] > bh_m["Max Drawdown"]

    insights = [
        (
            "Trend Capture Effectiveness",
            "The Moving Average Crossover strategy successfully identifies and rides major price trends. "
            "During strong bull phases it captures the majority of upside by staying long.",
        ),
        (
            "Sideways Market Underperformance",
            "In range-bound or choppy markets the strategy generates frequent false signals (whipsaws), "
            "leading to repeated small losses from entering and exiting positions without meaningful price movement.",
        ),
        (
            "Drawdown Protection",
            f"By exiting when the Death Cross occurs, the strategy's max drawdown is "
            f"**{strat_m['Max Drawdown']*100:.2f}%** vs Buy & Hold's "
            f"**{bh_m['Max Drawdown']*100:.2f}%**. "
            + ("This indicates better downside protection." if dd_better
               else "In this period Buy & Hold had a shallower drawdown, suggesting the strategy's exit timing lagged."),
        ),
        (
            "Signal Lag",
            f"The {short_window}/{long_window}-day crossover is inherently lagging. By the time a Golden Cross "
            "is confirmed the asset has often already moved significantly, meaning the strategy misses the initial "
            "phase of reversals in both directions.",
        ) if strategy_choice in ("Moving Average Crossover", "MA + RSI") else (
            "Strategy Lag",
            "Systematic strategies react to past prices; entries and exits occur after the move has started.",
        ),
        (
            "Risk-Adjusted Returns",
            f"Strategy Sharpe Ratio: **{strat_m['Sharpe Ratio']:.3f}** vs Buy & Hold: **{bh_m['Sharpe Ratio']:.3f}**. "
            + ("The strategy delivers superior risk-adjusted returns." if sharpe_better
               else "Buy & Hold achieved better risk-adjusted returns in this period."),
        ),
        (
            "Trade Frequency",
            f"The strategy generated **{len(buy_dates)} buy** and **{len(sell_dates)} sell** signals over the period, "
            "making it suitable for a low-turnover portfolio with minimal transaction costs.",
        ),
        (
            "Regime Dependency",
            "Performance is highly dependent on market regime. The strategy is most effective in trending environments "
            "and least effective in mean-reverting or volatile sideways markets. A regime-detection overlay could "
            "significantly improve results.",
        ),
    ]

    for i, (title, body) in enumerate(insights, 1):
        with st.expander(f"**{i}. {title}**", expanded=True):
            st.markdown(body)

# ──────────────────── TAB 5 : OPTIMIZE (Heatmap — MA strategies) ─────────────────────
@st.cache_data(show_spinner=False)
def compute_sharpe_grid(ticker_str, start_str, end_str, short_list, long_list, cap):
    """Compute Sharpe for each (short, long) pair using MA Crossover strategy."""
    raw = download_data(ticker_str, start_str, end_str)
    if raw.empty:
        return np.full((len(short_list), len(long_list)), np.nan)
    results = []
    for sw in short_list:
        row = []
        for lw in long_list:
            if sw >= lw:
                row.append(np.nan)
                continue
            params = {"short_window": sw, "long_window": lw, "rsi_period": 14}
            df_strat = apply_strategy(raw, "Moving Average Crossover", params)
            bt = backtest_strategy(df_strat, cap, transaction_cost_pct=0.0, use_transaction_cost=False)
            if bt.empty:
                row.append(np.nan)
                continue
            m = calculate_metrics(bt["Strategy_Return"], "")
            row.append(m["Sharpe Ratio"])
        results.append(row)
    return np.array(results)

with tabs[5]:
    st.markdown("### Parameter optimization")
    st.markdown("Heatmap: **Short MA** × **Long MA** → color = **Sharpe Ratio**. Uses **Moving Average Crossover** strategy. Higher (brighter) is better.")
    short_range = st.slider("Short MA range", 10, 80, (20, 60), step=5, key="opt_short")
    long_range = st.slider("Long MA range", 80, 300, (120, 220), step=10, key="opt_long")
    short_list = list(range(short_range[0], short_range[1] + 1, 5))
    long_list = list(range(long_range[0], long_range[1] + 1, 10))
    if short_list and long_list:
        with st.spinner("Computing Sharpe grid…"):
            grid = compute_sharpe_grid(ticker, str(start_date), str(end_date), short_list, long_list, initial_capital)
        fig_heat = go.Figure(data=go.Heatmap(
            z=grid, x=long_list, y=short_list,
            colorscale="RdYlGn", zmid=0,
            colorbar=dict(title="Sharpe"),
            hovertemplate="Short %{y} · Long %{x}<br>Sharpe: %{z:.3f}<extra></extra>",
        ))
        fig_heat.update_layout(
            title=f"{ticker} — Sharpe by MA parameters",
            xaxis_title="Long MA (days)",
            yaxis_title="Short MA (days)",
            template="plotly_dark",
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        try:
            best_flat = int(np.nanargmax(grid))
            best_short = short_list[best_flat // len(long_list)]
            best_long = long_list[best_flat % len(long_list)]
            st.success(f"Best in grid: Short **{best_short}** · Long **{best_long}** (Sharpe ≈ {np.nanmax(grid):.3f})")
        except Exception:
            st.info("No valid (Short < Long) pairs in selected range.")

# ──────────────────── TAB 6 : ABOUT (Limitations + Footer) ─────────────────────
with tabs[6]:
    st.markdown("### Limitations")

    limitations = [
        ("No Transaction Costs",
         "Real-world commissions and fees would reduce returns. Each buy/sell incurs a cost "
         "(typically $0.01–$0.03 per share for institutional, higher for retail)."),
        ("No Slippage",
         "We assume execution at the exact closing price. In practice, market orders experience "
         "slippage — the difference between expected and actual execution price."),
        ("No Intraday Execution Modeling",
         "Signals are generated at the close but assume instantaneous execution. A realistic model "
         "would use next-day open prices."),
        ("Past Performance ≠ Future Results",
         "Historical backtests do not guarantee future profitability. Market microstructure, liquidity "
         "conditions, and macroeconomic factors evolve."),
        ("Single Indicator Strategy",
         "Relying solely on moving average crossovers ignores valuable information from volume, volatility, "
         "fundamentals, and alternative data sources."),
        ("Survivorship Bias",
         f"We selected {ticker} — a highly liquid and successful stock. Testing on delisted or "
         "underperforming stocks would give a more honest assessment."),
        ("No Risk Management",
         "There are no stop-loss orders, position sizing rules, or portfolio-level risk controls in this "
         "simplified backtest."),
    ]

    for title, desc in limitations:
        with st.expander(f"**{title}**", expanded=True):
            st.markdown(desc)

    st.markdown("---")
    st.markdown(
        """
    <div class="footer-bar">
        <strong>Built by Arnav Gupta</strong> · Quantitative Trading Project · Not Investment Advice<br>
        <small>Streamlit & Plotly · Data via Yahoo Finance (yfinance)</small>
    </div>
    """,
        unsafe_allow_html=True,
    )
