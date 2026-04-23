#!/usr/bin/env python3
import yfinance as yf
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

def backtest_multiple_strategies(ticker, start="2020-01-01", end=None):
    if end is None:
        end = datetime.now().strftime('%Y-%m-%d')
    # Download data
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")
    
    # Handle MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    close = df['Close']
    returns = close.pct_change().dropna()
    results = []
    
    # Strategy 1: SMA Crossover (50/200)
    sma_fast = close.rolling(50).mean()
    sma_slow = close.rolling(200).mean()
    position = (sma_fast > sma_slow).astype(float)
    
    # Align returns with position (drop first row of position to match returns)
    position_aligned = position.iloc[1:].values
    
    strategy_returns = returns.values * position_aligned
    strategy_returns = pd.Series(strategy_returns, index=returns.index)
    cumulative = (1 + strategy_returns).cumprod()
    
    total_return = float((cumulative.iloc[-1] - 1) * 100)
    sharpe = float((strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252)) if len(strategy_returns) > 0 else 0
    max_dd = float(((cumulative / cumulative.cummax()) - 1).min() * 100)
    
    results.append({
        "strategy": "SMA_50_200",
        "return": total_return,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "win": total_return > 0
    })
    
    # Strategy 2: RSI Mean Reversion
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    position = ((rsi < 30).astype(int) - (rsi > 70).astype(int)).clip(lower=0).astype(float)
    position_aligned = position.iloc[1:].values
    
    strategy_returns = returns.values * position_aligned
    strategy_returns = pd.Series(strategy_returns, index=returns.index)
    cumulative = (1 + strategy_returns).cumprod()
    
    total_return = float((cumulative.iloc[-1] - 1) * 100)
    sharpe = float((strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252)) if len(strategy_returns) > 0 else 0
    max_dd = float(((cumulative / cumulative.cummax()) - 1).min() * 100)
    
    results.append({
        "strategy": "RSI_Mean_Reversion",
        "return": total_return,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "win": total_return > 0
    })
    
    # Strategy 3: Momentum (20-day)
    momentum = close.pct_change(20)
    position = (momentum > 0).astype(float)
    position_aligned = position.iloc[1:].values
    
    strategy_returns = returns.values * position_aligned
    strategy_returns = pd.Series(strategy_returns, index=returns.index)
    cumulative = (1 + strategy_returns).cumprod()
    
    total_return = float((cumulative.iloc[-1] - 1) * 100)
    sharpe = float((strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252)) if len(strategy_returns) > 0 else 0
    max_dd = float(((cumulative / cumulative.cummax()) - 1).min() * 100)
    
    results.append({
        "strategy": "Momentum_20d",
        "return": total_return,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "win": total_return > 0
    })
    
    # Find best strategy
    best = max(results, key=lambda x: x['return'])
    
    # Output
    print(f"\n{'='*70}")
    print(f"BACKTEST RESULTS: {ticker} ({start} to {end})")
    print(f"{'='*70}")
    print(f"\n{'Strategy':<25} {'Return':>10} {'Sharpe':>10} {'Max DD':>10} {'Result':>8}")
    print(f"{'-'*70}")
    
    for r in results:
        result_str = "WIN" if r['win'] else "LOSS"
        print(f"{r['strategy']:<25} {r['return']:>9.2f}% {r['sharpe']:>10.2f} {r['max_dd']:>9.2f}% {result_str:>8}")
    
    print(f"\n{'='*70}")
    print(f"BEST STRATEGY: {best['strategy']}")
    print(f"Return: {best['return']:.2f}% | Sharpe: {best['sharpe']:.2f} | Max DD: {best['max_dd']:.2f}%")
    
    winning_strategies = sum(1 for r in results if r['win'])
    print(f"\nSUMMARY: {winning_strategies}/{len(results)} strategies profitable")
    
    if best['return'] > 0 and best['sharpe'] > 1:
        conviction = "STRONG BUY"
    elif best['return'] > 0:
        conviction = "BUY"
    elif best['return'] < -10:
        conviction = "STRONG SELL"
    else:
        conviction = "SELL"
    
    print(f"\n{'='*70}")
    print(f"BACKTEST CONVICTION: {conviction}")
    print(f"{'='*70}\n")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest multiple strategies (decisive output)")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--start", default="2020-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2026-04-23", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    backtest_multiple_strategies(args.ticker, args.start, args.end)
