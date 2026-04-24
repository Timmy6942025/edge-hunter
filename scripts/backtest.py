#!/usr/bin/env python3
"""
Backtesting Engine - Strict Quant Rules Applied
1. NO look-ahead bias (shift(1) rule)
2. Mandatory friction (fees + slippage)
3. Correct math (log returns or fractional compounding)
4. Sanity checks (tripwires for impossible metrics)
5. Baseline benchmark (Buy & Hold comparison)
"""
import yfinance as yf
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data

# STRICT CONSTANTS
EXCHANGE_FEE = 0.001  # 0.1% fee per transaction (entry AND exit)
SLIPPAGE = 0.0005   # 0.05% slippage per trade
MAX_LEVERAGE = 1.0  # No leverage allowed (cap at 1x)

def calculate_log_returns(close_prices, positions):
    """
    Calculate log returns with proper compounding.
    positions: shift(1) applied (signal from yesterday, traded today at open)
    """
    # Log returns = ln(close_t / close_t-1)
    log_returns = np.log(close_prices / close_prices.shift(1))

    # Strategy returns = position_{t-1} * log_return_t
    # (position decided yesterday, executed today)
    strategy_log_returns = positions.shift(1) * log_returns

    # Convert back to arithmetic for cumulative
    cumulative = np.exp(strategy_log_returns.cumsum()) - 1

    return strategy_log_returns, cumulative

def apply_friction(returns, entry_signals, exit_signals):
    """
    Apply exchange fees and slippage to returns.
    Fees apply on entry AND exit.
    Slippage applies to both entry and exit prices.
    """
    # Calculate number of trades
    trades = (entry_signals.astype(int) + exit_signals.astype(int)).clip(0, 1)
    num_trades = trades.sum()

    # Apply friction to returns
    # Fee: 0.1% per transaction (entry + exit = 0.2% per round trip)
    # Slippage: 0.05% per trade
    total_friction = (EXCHANGE_FEE * 2 + SLIPPAGE * 2)  # Round trip friction

    # Deduct friction from returns on days we trade
    friction_cost = trades * total_friction
    returns_after_fees = returns - friction_cost

    return returns_after_fees, num_trades

def backtest_strategy(ticker, start="2020-01-01", end=None):
    if end is None:
        end = datetime.now().strftime('%Y-%m-%d')

    # Download data
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")

    # Flatten MultiIndex columns (yfinance compat)
    df = flatten_yf_data(df)

    close = df['Close']
    open_price = df['Open'] if 'Open' in df.columns else close

    returns = close.pct_change().dropna()
    results = []

    # ==========================================================================
    # STRATEGY 1: SMA Crossover (50/200) - NO LOOK-AHEAD BIAS
    # ==========================================================================
    sma_fast = close.rolling(50).mean()
    sma_slow = close.rolling(200).mean()

    # Signal generated at CLOSE of day t
    raw_signal = (sma_fast > sma_slow).astype(float)

    # CRITICAL: Shift signal - trade at OPEN of NEXT day (t+1)
    # This eliminates look-ahead bias
    position = raw_signal.shift(1)
    position = position.fillna(0)

    # Calculate returns with proper math (log returns)
    strategy_returns = position * returns

    # Apply friction (fees + slippage)
    entry_signals = (position > position.shift(1)) & (position.shift(1) == 0)
    exit_signals = (position < position.shift(1)) & (position.shift(1) == 1)
    strategy_returns, num_trades = apply_friction(strategy_returns, entry_signals, exit_signals)

    # Cap leverage at 1x
    strategy_returns = strategy_returns.clip(-MAX_LEVERAGE, MAX_LEVERAGE)

    # Cumulative returns (fractional compounding)
    cumulative = (1 + strategy_returns).cumprod()
    total_return = (cumulative.iloc[-1] - 1) * 100

    std_sr = strategy_returns.std()
    sharpe = float((strategy_returns.mean() / std_sr) * np.sqrt(252)) if std_sr > 0 else 0
    max_dd = float(((cumulative / cumulative.cummax()) - 1).min() * 100)

    # Win rate calculation
    winning_days = (strategy_returns > 0).sum()
    total_days = (strategy_returns != 0).sum()
    win_rate = (winning_days / total_days * 100) if total_days > 0 else 0

    results.append({
        "strategy": "SMA_50_200",
        "return": float(total_return),
        "sharpe": sharpe,
        "max_dd": max_dd,
        "win_rate": float(win_rate),
        "num_trades": int(num_trades),
        "win": total_return > 0
    })

    # ==========================================================================
    # STRATEGY 2: RSI Mean Reversion - NO LOOK-AHEAD BIAS
    # ==========================================================================
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Signal: Buy when RSI < 30, Sell when RSI > 70
    raw_signal = ((rsi < 30).astype(int) - (rsi > 70).astype(int)).clip(lower=0).astype(float)

    # Shift to avoid look-ahead
    position = raw_signal.shift(1).fillna(0)

    strategy_returns = position * returns
    entry_signals = (position > position.shift(1)) & (position.shift(1) == 0)
    exit_signals = (position < position.shift(1)) & (position.shift(1) == 1)
    strategy_returns, num_trades = apply_friction(strategy_returns, entry_signals, exit_signals)
    strategy_returns = strategy_returns.clip(-MAX_LEVERAGE, MAX_LEVERAGE)

    cumulative = (1 + strategy_returns).cumprod()
    total_return = (cumulative.iloc[-1] - 1) * 100
    std_sr = strategy_returns.std()
    sharpe = float((strategy_returns.mean() / std_sr) * np.sqrt(252)) if std_sr > 0 else 0
    max_dd = float(((cumulative / cumulative.cummax()) - 1).min() * 100)

    winning_days = (strategy_returns > 0).sum()
    total_days = (strategy_returns != 0).sum()
    win_rate = (winning_days / total_days * 100) if total_days > 0 else 0

    results.append({
        "strategy": "RSI_Mean_Reversion",
        "return": float(total_return),
        "sharpe": sharpe,
        "max_dd": max_dd,
        "win_rate": float(win_rate),
        "num_trades": int(num_trades),
        "win": total_return > 0
    })

    # ==========================================================================
    # STRATEGY 3: Momentum (20-day) - NO LOOK-AHEAD BIAS
    # ==========================================================================
    momentum = close.pct_change(20)
    raw_signal = (momentum > 0).astype(float)

    # Shift to avoid look-ahead
    position = raw_signal.shift(1).fillna(0)

    strategy_returns = position * returns
    entry_signals = (position > position.shift(1)) & (position.shift(1) == 0)
    exit_signals = (position < position.shift(1)) & (position.shift(1) == 1)
    strategy_returns, num_trades = apply_friction(strategy_returns, entry_signals, exit_signals)
    strategy_returns = strategy_returns.clip(-MAX_LEVERAGE, MAX_LEVERAGE)

    cumulative = (1 + strategy_returns).cumprod()
    total_return = (cumulative.iloc[-1] - 1) * 100
    std_sr = strategy_returns.std()
    sharpe = float((strategy_returns.mean() / std_sr) * np.sqrt(252)) if std_sr > 0 else 0
    max_dd = float(((cumulative / cumulative.cummax()) - 1).min() * 100)

    winning_days = (strategy_returns > 0).sum()
    total_days = (strategy_returns != 0).sum()
    win_rate = (winning_days / total_days * 100) if total_days > 0 else 0

    results.append({
        "strategy": "Momentum_20d",
        "return": float(total_return),
        "sharpe": sharpe,
        "max_dd": max_dd,
        "win_rate": float(win_rate),
        "num_trades": int(num_trades),
        "win": total_return > 0
    })

    # ==========================================================================
    # BASELINE: Buy and Hold (for alpha comparison)
    # ==========================================================================
    buy_hold_return = (close.iloc[-1] / close.iloc[0] - 1) * 100
    buy_hold_returns = returns  # Just hold the asset
    bh_std = buy_hold_returns.std()
    buy_hold_sharpe = float((buy_hold_returns.mean() / bh_std) * np.sqrt(252)) if bh_std > 0 else 0
    bh_cumulative = (1 + buy_hold_returns).cumprod()
    buy_hold_max_dd = float(((bh_cumulative / bh_cumulative.cummax()) - 1).min() * 100)

    # ==========================================================================
    # OUTPUT
    # ==========================================================================
    print(f"\n{'='*70}")
    print(f"BACKTEST RESULTS: {ticker} ({start} to {end})")
    print(f"Friction Applied: {EXCHANGE_FEE*100:.1f}% fee + {SLIPPAGE*100:.1f}% slippage per trade")
    print(f"Max Leverage Capped: {MAX_LEVERAGE:.1f}x")
    print(f"{'='*70}")

    print(f"\n{'Strategy':<25} {'Return':>10} {'Sharpe':>10} {'Max DD':>10} {'Win%':>8} {'Trades':>8} {'Alpha':>10}")
    print(f"{'-'*70}")

    for r in results:
        alpha = r['return'] - buy_hold_return
        result_str = "WIN" if r['win'] else "LOSS"
        print(
            f"{r['strategy']:<25} {r['return']:>9.2f}% "
            f"{r['sharpe']:>10.2f} {r['max_dd']:>9.2f}% "
            f"{r['win_rate']:>7.1f}% {r['num_trades']:>8} {alpha:>+9.2f}%"
        )

    # Baseline
    print(
        f"{'Buy & Hold (Baseline)':<25} {buy_hold_return:>9.2f}% "
        f"{buy_hold_sharpe:>10.2f} {buy_hold_max_dd:>9.2f}% "
        f"{'N/A':>8} {'N/A':>8} {'0.00%':>10}"
    )

    # Find best strategy
    best = max(results, key=lambda x: x['return'])

    print(f"\n{'='*70}")
    print(f"BEST STRATEGY: {best['strategy']}")
    print(
        f"Return: {best['return']:.2f}% | "
        f"Sharpe: {best['sharpe']:.2f} | "
        f"Max DD: {best['max_dd']:.2f}%"
    )
    print(
        f"Win Rate: {best['win_rate']:.1f}% | "
        f"Trades: {best['num_trades']} | "
        f"Alpha vs Buy&Hold: {best['return'] - buy_hold_return:+.2f}%"
    )

    # ==========================================================================
    # SANITY CHECK TRIPWIRES
    # ==========================================================================
    warnings = []

    # Win Rate > 80% (statistically improbable)
    if best['win_rate'] > 80:
        warnings.append("WARNING: Win Rate >80% - Statistically improbable. Check for look-ahead bias or overfitting.")

    # Sharpe > 3.5 (extremely rare in real markets)
    if best['sharpe'] > 3.5:
        warnings.append("WARNING: Sharpe Ratio >3.5 - Extremely rare. Likely overfitting or forward-looking bias.")

    # ROI > 5000% over short timeframe (impossible without leverage)
    days_of_data = (datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days
    if best['return'] > 5000 and days_of_data < 365 * 5:
        warnings.append("WARNING: ROI >5000% in <5 years - Impossible without extreme leverage or data snooping.")

    # Check for negative trades (shouldn't happen with long-only)
    if best['num_trades'] == 0:
        warnings.append("WARNING: No trades executed - Check position logic and shift() rule.")

    if warnings:
        print(f"\n{'!'*70}")
        print("SANITY CHECK TRIPWIRES TRIGGERED:")
        for w in warnings:
            print(f"  ⚠ {w}")
        print(f"{'!'*70}\n")
        results.append({"warnings": warnings})

    # Conviction
    winning_strategies = sum(1 for r in results if r.get('win', False) and isinstance(r.get('return'), float))

    if best['return'] > buy_hold_return and best['sharpe'] > buy_hold_sharpe and best['sharpe'] > 1:
        conviction = "STRONG BUY (Alpha Generated)"
    elif best['return'] > buy_hold_return:
        conviction = "BUY (Positive Alpha)"
    elif best['return'] < buy_hold_return - 10:
        conviction = "STRONG SELL (Underperforms Buy&Hold)"
    else:
        conviction = "SELL (No Alpha)"

    print(f"\n{'='*70}")
    print(f"BACKTEST CONVICTION: {conviction}")
    bh_alpha = best['return'] - buy_hold_return
    print(f"Alpha Generated: {bh_alpha:+.2f}% vs Buy&Hold")
    print(f"{'='*70}\n")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest with strict quant rules (no look-ahead, with friction)")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--start", default="2020-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD, defaults to today)")
    args = parser.parse_args()
    backtest_strategy(args.ticker, args.start, args.end)
