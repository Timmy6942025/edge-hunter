#!/usr/bin/env python3
import yfinance as yf
import numpy as np
import argparse
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, extract_price_data
from datetime import datetime


def calculate_comprehensive_risk(ticker, start="2020-01-01", end=None):
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")

    # Flatten MultiIndex columns (yfinance compat)
    df = flatten_yf_data(df)

    close = df["Close"]
    returns = close.pct_change().dropna()

    # Basic metrics
    ann_factor = 252**0.5
    total_return = float((close.iloc[-1] / close.iloc[0] - 1) * 100)

    mean_return = float(returns.mean() * 252 * 100)
    volatility = float(returns.std() * np.sqrt(252) * 100)

    std_val = float(returns.std())
    sharpe = float((returns.mean() / returns.std()) * ann_factor) if std_val > 0 else 0

    downside_returns = returns[returns < 0]
    if len(downside_returns) > 0:
        sortino = float((returns.mean() / downside_returns.std()) * ann_factor)
    else:
        sortino = 0

    cummax = close.cummax()
    drawdown = close / cummax - 1
    max_dd = float(drawdown.min() * 100)
    current_dd = float(drawdown.iloc[-1] * 100)

    # VaR (Value at Risk) - 95% confidence
    var_95 = float(np.percentile(returns.values, 5) * 100)

    # CVaR (Conditional VaR)
    cvar_95 = float(returns[returns <= np.percentile(returns.values, 5)].mean() * 100)

    # Beta (vs S&P 500)
    try:
        spy = extract_price_data(yf.download("SPY", start=start, end=end, progress=False), "Close")
        spy_returns = spy.pct_change().dropna()

        # Align the series
        aligned_returns = returns.reindex(spy_returns.index, method=None)
        spy_returns_aligned = spy_returns.reindex(returns.index, method=None)

        # Drop NaNs and calculate beta
        valid_idx = aligned_returns.notna() & spy_returns_aligned.notna()
        if valid_idx.sum() > 10:
            cov = np.cov(aligned_returns[valid_idx], spy_returns_aligned[valid_idx])
            beta = float(cov[0, 1] / np.var(spy_returns_aligned[valid_idx]))
        else:
            beta = 1.0
    except Exception:
        beta = 1.0

    # Win rate
    positive_days = (returns > 0).sum()
    win_rate = float((positive_days / len(returns)) * 100)

    # Average win/loss
    avg_win = float(returns[returns > 0].mean() * 100) if (returns > 0).any() else 0
    avg_loss = float(returns[returns < 0].mean() * 100) if (returns < 0).any() else 0
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float("inf")

    # Calmar ratio
    calmar = (mean_return / abs(max_dd)) if max_dd != 0 else 0

    # Risk assessment
    if sharpe > 1.5 and max_dd > -20 and beta < 1.2:
        risk_rating = "LOW RISK / HIGH QUALITY"
    elif sharpe > 1.0 and max_dd > -30:
        risk_rating = "MODERATE RISK"
    elif sharpe > 0.5:
        risk_rating = "HIGH RISK / SPECULATIVE"
    else:
        risk_rating = "VERY HIGH RISK / AVOID"

    # Output
    print(f"\n{'=' * 70}")
    print(f"COMPREHENSIVE RISK ANALYSIS: {ticker}")
    print(f"{'=' * 70}")

    print(f"\nPERFORMANCE METRICS:")
    print(f"  Total Return: {total_return:.2f}%")
    print(f"  Annualized Return: {mean_return:.2f}%")
    print(f"  Annualized Volatility: {volatility:.2f}%")

    print(f"\nRISK-ADJUSTED METRICS:")
    print(f"  Sharpe Ratio: {sharpe:.2f}")
    print(f"  Sortino Ratio: {sortino:.2f}")
    print(f"  Calmar Ratio: {calmar:.2f}")

    print(f"\nDRAWDOWN ANALYSIS:")
    print(f"  Max Drawdown: {max_dd:.2f}%")
    print(f"  Current Drawdown: {current_dd:.2f}%")

    print(f"\nDOWNSIDE RISK:")
    print(f"  VaR (95%): {var_95:.2f}%")
    print(f"  CVaR (95%): {cvar_95:.2f}%")

    print(f"\nMARKET EXPOSURE:")
    print(f"  Beta (vs SPY): {beta:.2f}")

    print(f"\nTRADING STATS:")
    print(f"  Win Rate: {win_rate:.2f}%")
    print(f"  Avg Win: {avg_win:.3f}%")
    print(f"  Avg Loss: {avg_loss:.3f}%")
    print(f"  Profit Factor: {profit_factor:.2f}")

    print(f"\n{'=' * 70}")
    print(f"RISK RATING: {risk_rating}")
    print(f"{'=' * 70}\n")

    return {"sharpe": sharpe, "sortino": sortino, "max_dd": max_dd, "risk_rating": risk_rating}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comprehensive risk analysis")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--start", default="2020-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2026-04-23", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    calculate_comprehensive_risk(args.ticker, args.start, args.end)
