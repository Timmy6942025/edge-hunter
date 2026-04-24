#!/usr/bin/env python3
"""
Short Squeeze Analysis Script (Professional Quant)
================================================
- Short interest tracking
- Days to cover calculation
- Squeeze potential scoring
- Short ratio analysis
"""

import argparse
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, safe_float
import warnings

warnings.filterwarnings("ignore")


def analyze_short_squeeze(ticker):
    """Comprehensive short squeeze analysis"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        data = yf.download(ticker, period="1mo", progress=False)
        if data.empty:
            return {"error": "No price data"}

        data = flatten_yf_data(data)

        # Short metrics
        short_ratio = info.get("shortRatio", 0) or 0
        short_float = info.get("shortPercentOfFloat", 0) or 0
        shares_short = info.get("sharesShort", 0) or 0
        avg_volume = info.get("averageVolume", 0) or 0

        # Calculate days to cover
        days_to_cover = short_ratio if short_ratio > 0 else 0

        # Get price metrics
        current_price = float(data["Close"].iloc[-1]) if not data.empty else 0
        high_52w = info.get("fiftyTwoWeekHigh", 0) or 0
        low_52w = info.get("fiftyTwoWeekLow", 0) or 0

        # Calculate price position
        if high_52w > low_52w:
            price_position = ((current_price - low_52w) / (high_52w - low_52w)) * 100
        else:
            price_position = 50

        # Recent price momentum
        returns_5d = ((current_price / float(data["Close"].iloc[-6])) - 1) * 100 if len(data) > 5 else 0
        returns_1m = ((current_price / float(data["Close"].iloc[-22])) - 1) * 100 if len(data) > 21 else 0

        return {
            "ticker": ticker,
            "short_ratio": float(short_ratio),
            "short_float_pct": float(short_float * 100) if short_float else 0,
            "shares_short": float(shares_short),
            "avg_volume": float(avg_volume),
            "days_to_cover": float(days_to_cover),
            "current_price": float(current_price),
            "high_52w": float(high_52w),
            "low_52w": float(low_52w),
            "price_position": float(price_position),
            "returns_5d": float(returns_5d),
            "returns_1m": float(returns_1m),
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_squeeze_score(data):
    """Calculate short squeeze potential score (0-100)"""
    score = 0

    # Short interest component (max 30 points)
    if data["short_float_pct"] > 20:
        score += 30
    elif data["short_float_pct"] > 15:
        score += 25
    elif data["short_float_pct"] > 10:
        score += 20
    elif data["short_float_pct"] > 5:
        score += 10
    else:
        score += 5

    # Days to cover component (max 25 points)
    if data["days_to_cover"] > 10:
        score += 25
    elif data["days_to_cover"] > 7:
        score += 20
    elif data["days_to_cover"] > 5:
        score += 15
    elif data["days_to_cover"] > 3:
        score += 10
    else:
        score += 5

    # Price position component (max 20 points) - Near highs = more squeeze potential
    if data["price_position"] > 90:
        score += 20
    elif data["price_position"] > 80:
        score += 15
    elif data["price_position"] > 70:
        score += 10
    else:
        score += 5

    # Recent momentum component (max 25 points)
    if data["returns_5d"] > 10:
        score += 15
    elif data["returns_5d"] > 5:
        score += 10
    elif data["returns_5d"] > 0:
        score += 5

    if data["returns_1m"] > 20:
        score += 10
    elif data["returns_1m"] > 10:
        score += 7
    elif data["returns_1m"] > 0:
        score += 3

    return min(100, score)


def main():
    parser = argparse.ArgumentParser(description="Short Squeeze Analysis")
    parser.add_argument("tickers", nargs="+", help="Tickers to analyze")
    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"SHORT SQUEEZE ANALYSIS")
    print(f"{'=' * 70}")
    print(f"Tickers: {args.tickers}")

    results = []
    for ticker in args.tickers:
        print(f"   Analyzing {ticker}...", end=" ")
        data = analyze_short_squeeze(ticker)
        if "error" not in data:
            data["squeeze_score"] = calculate_squeeze_score(data)
            results.append(data)
            print("✅")
        else:
            print(f"❌ ({data.get('error', 'unknown')})")

    if not results:
        print("❌ No data available")
        return

    print(f"\n{'─' * 70}")
    print(f"SHORT INTEREST METRICS")
    print(f"{'─' * 70}")

    print(f"\n{'┌' + '─' * 68 + '┐'}")
    print(f"│{'Ticker':<8} {'Short %':>10} {'Days to Cover':>14} {'5D Mom':>10} {'Score':>8}│")
    print(f"├{'─' * 68 + '┤'}")

    for r in sorted(results, key=lambda x: x["squeeze_score"], reverse=True):
        score_bar = "█" * int(r["squeeze_score"] / 10)
        print(
            f"│{r['ticker']:<8} {r['short_float_pct']:>9.1f}% "
            f"{r['days_to_cover']:>13.1f} "
            f"{r['returns_5d']:>+9.1f}% {r['squeeze_score']:>7}{score_bar}│"
        )
    print(f"└{'─' * 68 + '┘'}")

    print(f"\n{'─' * 70}")
    print(f"SQUEEZE POTENTIAL RANKING")
    print(f"{'─' * 70}")

    results.sort(key=lambda x: x["squeeze_score"], reverse=True)

    for idx, r in enumerate(results, 1):
        if r["squeeze_score"] >= 70:
            level = "🟢 HIGH"
        elif r["squeeze_score"] >= 50:
            level = "🟡 MEDIUM"
        else:
            level = "⚪ LOW"

        print(f"\n   {idx}. {r['ticker']} - Score: {r['squeeze_score']}/100 ({level})")
        print(f"      Short Float: {r['short_float_pct']:.1f}%")
        print(f"      Days to Cover: {r['days_to_cover']:.1f}")
        print(f"      5D Return: {r['returns_5d']:+.1f}%")
        print(f"      52W Position: {r['price_position']:.0f}%")

    # Best squeeze candidate
    print(f"\n{'─' * 70}")
    print(f"🏆 TOP SQUEEZE CANDIDATE")
    print(f"{'─' * 70}")

    best = results[0]
    print(f"   {best['ticker']} - Squeeze Score: {best['squeeze_score']}/100")

    if best["squeeze_score"] >= 70:
        print(f"   📊 HIGH SHORT SQUEEZE POTENTIAL")
        print(f"   ⚠️ Warning: High short interest + price momentum = squeeze risk")
    elif best["squeeze_score"] >= 50:
        print(f"   📊 MODERATE SHORT SQUEEZE POTENTIAL")


if __name__ == "__main__":
    main()
