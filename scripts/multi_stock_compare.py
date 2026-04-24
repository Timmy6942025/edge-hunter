#!/usr/bin/env python3
"""
Multi-Stock Compare Script (Professional Quant)
================================================
- Side-by-side comparison of multiple tickers
- Performance ranking
- Risk-adjusted metrics
- Visual comparison tables
"""

import argparse
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, safe_float
import warnings

warnings.filterwarnings("ignore")


def analyze_ticker(ticker, period="1y"):
    """Analyze single ticker"""
    try:
        data = yf.download(ticker, period=period, progress=False)
        data = flatten_yf_data(data)

        if data.empty:
            return None

        info = yf.Ticker(ticker).info

        current = float(data["Close"].iloc[-1])
        start = safe_float(data["Close"].iloc[0])

        # Calculate returns
        close_last = safe_float(data["Close"].iloc[-1])
        returns_1d = ((close_last / safe_float(data["Close"].iloc[-2])) - 1) * 100 if len(data) > 1 else 0
        returns_1w = ((close_last / safe_float(data["Close"].iloc[-6])) - 1) * 100 if len(data) > 5 else 0
        returns_1m = ((close_last / safe_float(data["Close"].iloc[-22])) - 1) * 100 if len(data) > 21 else 0
        returns_3m = ((current / safe_float(data["Close"].iloc[-63])) - 1) * 100 if len(data) > 62 else 0
        returns_1y = ((current / start) - 1) * 100

        # Calculate volatility
        daily_returns = data["Close"].pct_change().dropna()
        volatility_30d = daily_returns.tail(30).std() * np.sqrt(252) * 100
        volatility_1y = daily_returns.std() * np.sqrt(252) * 100

        # Calculate max drawdown
        rolling_max = data["Close"].cummax()
        drawdown = (data["Close"] - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()

        # Sharpe ratio
        sharpe = ((returns_1y / 100 - 0.05) / (volatility_1y / 100)) if volatility_1y > 0 else 0

        # Get fundamentals
        pe = info.get("trailingPE", 0) or 0
        pb = info.get("priceToBook", 0) or 0
        dividend = info.get("dividendYield", 0) or 0
        market_cap = info.get("marketCap", 0) or 0
        volume = info.get("averageVolume", 0) or 0

        return {
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "current": current,
            "returns_1d": returns_1d,
            "returns_1w": returns_1w,
            "returns_1m": returns_1m,
            "returns_3m": returns_3m,
            "returns_1y": returns_1y,
            "volatility_30d": volatility_30d,
            "volatility_1y": volatility_1y,
            "max_drawdown": max_drawdown,
            "sharpe": sharpe,
            "pe": pe,
            "pb": pb,
            "dividend_yield": dividend * 100 if dividend else 0,
            "market_cap": market_cap,
            "volume": volume,
        }
    except Exception:
        return None


def calculate_score(ticker_data):
    """Calculate composite score for ranking"""
    score = 0

    score += min(40, ticker_data["returns_1y"] / 2)
    score += min(30, max(0, ticker_data["sharpe"] * 15))

    if ticker_data["volatility_1y"] < 20:
        score += 15
    elif ticker_data["volatility_1y"] < 30:
        score += 10
    else:
        score += 5

    if ticker_data["max_drawdown"] > -10:
        score += 15
    elif ticker_data["max_drawdown"] > -20:
        score += 10
    else:
        score += 5

    return score


def main():
    parser = argparse.ArgumentParser(description="Multi-Stock Comparison")
    parser.add_argument("tickers", nargs="+", help="Tickers to compare")
    parser.add_argument("--period", default="1y", help="Analysis period")
    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"MULTI-STOCK COMPARISON")
    print(f"{'=' * 70}")
    print(f"Tickers: {args.tickers}")

    print(f"\n📥 Analyzing {len(args.tickers)} tickers...")

    results = []
    for ticker in args.tickers:
        data = analyze_ticker(ticker, args.period)
        if data:
            data["score"] = calculate_score(data)
            results.append(data)
            print(f"   ✅ {ticker}")
        else:
            print(f"   ❌ {ticker} - Failed")

    if not results:
        print("❌ No valid tickers to compare")
        return

    # Performance table
    print(f"\n{'─' * 70}")
    print(f"PERFORMANCE COMPARISON")
    print(f"{'─' * 70}")

    print(f"\n{'┌' + '─' * 68 + '┐'}")
    print(f"│{'Ticker':<8} {'Price':>8} {'1D':>7} {'1W':>7} {'1M':>7} {'3M':>7} {'1Y':>7}│")
    print(f"├{'─' * 68 + '┤'}")

    for r in sorted(results, key=lambda x: x["returns_1y"], reverse=True):
        emoji_1d = "▲" if r["returns_1d"] > 0 else "▼"
        print(
            f"│{r['ticker']:<8} ${r['current']:<7.2f} "
            f"{r['returns_1d']:>+6.1f}%{emoji_1d} "
            f"{r['returns_1w']:>+6.1f}% {r['returns_1m']:>+6.1f}% "
            f"{r['returns_3m']:>+6.1f}% {r['returns_1y']:>+6.1f}%│"
        )
    print(f"└{'─' * 68 + '┘'}")

    # Risk metrics
    print(f"\n{'─' * 70}")
    print(f"RISK METRICS")
    print(f"{'─' * 70}")

    print(f"\n{'┌' + '─' * 68 + '┐'}")
    print(f"│{'Ticker':<8} {'Vol(30d)':>10} {'Vol(1Y)':>10} {'Max DD':>10} {'Sharpe':>8} {'Score':>7}│")
    print(f"├{'─' * 68 + '┤'}")

    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        print(
            f"│{r['ticker']:<8} "
            f"{r['volatility_30d']:>9.1f}% {r['volatility_1y']:>9.1f}% "
            f"{r['max_drawdown']:>9.1f}% {r['sharpe']:>7.2f} {r['score']:>6.1f}│"
        )
    print(f"└{'─' * 68 + '┘'}")

    # Fundamentals
    print(f"\n{'─' * 70}")
    print(f"VALUATION METRICS")
    print(f"{'─' * 70}")

    print(f"\n{'┌' + '─' * 68 + '┐'}")
    print(f"│{'Ticker':<8} {'P/E':>8} {'P/B':>8} {'Div Yield':>10} {'Mkt Cap':>12}│")
    print(f"├{'─' * 68 + '┤'}")

    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        mc = r["market_cap"]
        if mc > 1e12:
            mc_str = f"${mc / 1e12:.1f}T"
        elif mc > 1e9:
            mc_str = f"${mc / 1e9:.1f}B"
        else:
            mc_str = f"${mc / 1e6:.1f}M"

        div = r["dividend_yield"]
        print(f"│{r['ticker']:<8} {r['pe']:>8.1f} {r['pb']:>8.1f} {div:>9.2f}% {mc_str:>12}│")
    print(f"└{'─' * 68 + '┘'}")

    # Overall ranking
    print(f"\n{'─' * 70}")
    print(f"OVERALL RANKING (Risk-Adjusted)")
    print(f"{'─' * 70}")

    results.sort(key=lambda x: x["score"], reverse=True)

    for idx, r in enumerate(results, 1):
        medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else f"{idx}."))
        print(f"   {medal} {r['ticker']:<8} Score: {r['score']:6.1f} - ", end="")

        strengths = []
        if r["returns_1y"] > 20:
            strengths.append("Strong returns")
        if r["sharpe"] > 1:
            strengths.append("Good risk-adjusted")
        if r["volatility_1y"] < 25:
            strengths.append("Low volatility")
        if r["max_drawdown"] > -15:
            strengths.append("Defensive")

        print(", ".join(strengths) if strengths else "Balanced")

    print(f"\n{'─' * 70}")
    print(f"🏆 TOP PICK")
    print(f"{'─' * 70}")

    best = results[0]
    print(f"   {best['ticker']} - Score: {best['score']:6.1f}")
    print(f"   1Y Return: {best['returns_1y']:+.1f}%")
    print(f"   Sharpe: {best['sharpe']:.2f}")
    print(f"   Volatility: {best['volatility_1y']:.1f}%")
    print(f"   Max Drawdown: {best['max_drawdown']:.1f}%")


if __name__ == "__main__":
    main()
