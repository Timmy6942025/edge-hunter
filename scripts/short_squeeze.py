#!/usr/bin/env python3
r"""
Short Squeeze Analysis (edge-hunter)
====================================
- Short interest tracking + days to cover
- Cost-to-borrow estimation
- Squeeze potential scoring with threshold alerts
- Gamma exposure analysis (call/put open interest imbalance)
- Sector comparison

Usage:
    python short_squeeze.py GME AMC
    python short_squeeze.py GME --sector "Consumer Discretionary"
"""

import argparse
import numpy as np
import yfinance as yf
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, safe_float
import warnings

warnings.filterwarnings("ignore")


def get_gamma_exposure(ticker):
    """Fetch options chain and calculate gamma exposure imbalance."""
    try:
        stock = yf.Ticker(ticker)
        opt = stock.option_chain(date=None)
        if opt is None:
            return None
        calls = opt.calls
        puts = opt.puts
        call_oi = calls["openInterest"].sum() if "openInterest" in calls.columns else 0
        put_oi = puts["openInterest"].sum() if "openInterest" in puts.columns else 0
        total_oi = call_oi + put_oi
        if total_oi == 0:
            return None
        gamma_ratio = (call_oi - put_oi) / total_oi
        return {
            "call_oi": int(call_oi),
            "put_oi": int(put_oi),
            "gamma_ratio": gamma_ratio,
            "total_oi": int(total_oi),
        }
    except Exception:
        return None


def estimate_cost_to_borrow(days_to_cover, short_float_pct):
    """Estimate annualized cost-to-borrow from days-to-cover and short interest."""
    annual_turns = 252 / max(days_to_cover, 1)
    estimated_rate = min(short_float_pct / 10 * 0.05, 0.50)
    return estimated_rate


def squeeze_alert_level(short_float_pct, days_to_cover):
    """Determine squeeze alert level from short interest and days to cover."""
    if short_float_pct > 25:
        return "EXTREME", "🔴"
    elif short_float_pct >= 15 or (short_float_pct >= 5 and days_to_cover > 5):
        return "HIGH", "🟠"
    elif short_float_pct >= 5:
        return "MEDIUM", "🟡"
    else:
        return "LOW", "⚪"


def analyze_short_squeeze(ticker, sector=None):
    """Comprehensive short squeeze analysis with gamma and sector context."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        data = yf.download(ticker, period="1mo", progress=False)
        if data.empty:
            return {"error": "No price data"}
        data = flatten_yf_data(data)

        short_ratio = info.get("shortRatio", 0) or 0
        short_float = info.get("shortPercentOfFloat", 0) or 0
        shares_short = info.get("sharesShort", 0) or 0
        avg_volume = info.get("averageVolume", 0) or 0
        shares_outstanding = info.get("sharesOutstanding", 0) or 1
        days_to_cover = short_ratio if short_ratio > 0 else 0

        current_price = float(data["Close"].iloc[-1]) if not data.empty else 0
        high_52w = info.get("fiftyTwoWeekHigh", 0) or 0
        low_52w = info.get("fiftyTwoWeekLow", 0) or 0
        short_float_pct = float(short_float * 100) if short_float else 0

        if high_52w > low_52w:
            price_position = ((current_price - low_52w) / (high_52w - low_52w)) * 100
        else:
            price_position = 50

        returns_5d = ((current_price / float(data["Close"].iloc[-6])) - 1) * 100 if len(data) > 5 else 0
        returns_1m = ((current_price / float(data["Close"].iloc[-22])) - 1) * 100 if len(data) > 21 else 0

        alert_level, alert_emoji = squeeze_alert_level(short_float_pct, days_to_cover)
        gamma = get_gamma_exposure(ticker)
        cost_to_borrow = estimate_cost_to_borrow(days_to_cover, short_float_pct) if short_float_pct > 1 else 0

        return {
            "ticker": ticker,
            "short_ratio": float(short_ratio),
            "short_float_pct": short_float_pct,
            "shares_short": float(shares_short),
            "avg_volume": float(avg_volume),
            "days_to_cover": float(days_to_cover),
            "current_price": float(current_price),
            "high_52w": float(high_52w),
            "low_52w": float(low_52w),
            "price_position": float(price_position),
            "returns_5d": float(returns_5d),
            "returns_1m": float(returns_1m),
            "alert_level": alert_level,
            "alert_emoji": alert_emoji,
            "gamma": gamma,
            "cost_to_borrow": cost_to_borrow,
            "sector": sector,
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_squeeze_score(data):
    """Calculate short squeeze potential score (0-100)."""
    score = 0
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
    if data["price_position"] > 90:
        score += 20
    elif data["price_position"] > 80:
        score += 15
    elif data["price_position"] > 70:
        score += 10
    else:
        score += 5
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
    parser = argparse.ArgumentParser(description="Short Squeeze Analysis (edge-hunter)")
    parser.add_argument("tickers", nargs="+", help="Tickers to analyze")
    parser.add_argument("--sector", help="Sector for context (e.g., 'Consumer Discretionary')")
    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"SHORT SQUEEZE ANALYSIS (edge-hunter)")
    print(f"{'=' * 70}")
    print(f"Tickers: {args.tickers}")
    if args.sector:
        print(f"Sector: {args.sector}")

    results = []
    for ticker in args.tickers:
        print(f"   Analyzing {ticker}...", end=" ")
        data = analyze_short_squeeze(ticker, args.sector)
        if "error" not in data:
            data["squeeze_score"] = calculate_squeeze_score(data)
            results.append(data)
            print("Done")
        else:
            print(f"Failed ({data.get('error', 'unknown')})")

    if not results:
        print("[ERROR] No data available")
        return

    print(f"\n{'─' * 70}")
    print(f"SHORT INTEREST & SQUEEZE METRICS")
    print(f"{'─' * 70}")

    print(f"\n{'Ticker':<8} {'Short%':>8} {'DtC':>5} {'5D%':>7} {'Gamma':>7} {'Score':>6}  {'Level':<10}")
    print(f"{'─' * 68}")

    for r in sorted(results, key=lambda x: x["squeeze_score"], reverse=True):
        gamma_str = f"{(r['gamma']['gamma_ratio'] * 100):.0f}%" if r.get("gamma") else "N/A"
        print(
            f"{r['ticker']:<8} {r['short_float_pct']:>7.1f}% {r['days_to_cover']:>5.1f} "
            f"{r['returns_5d']:>+6.1f}% {gamma_str:>7} {r['squeeze_score']:>5} {r['alert_emoji']} {r['alert_level']:<9}"
        )

    print(f"\n{'─' * 70}")
    print(f"SQUEEZE POTENTIAL RANKING")
    print(f"{'─' * 70}")

    results.sort(key=lambda x: x["squeeze_score"], reverse=True)
    for idx, r in enumerate(results, 1):
        print(f"\n   {idx}. {r['ticker']} - Score: {r['squeeze_score']}/100")
        print(f"      Short Float: {r['short_float_pct']:.1f}% ({r['alert_emoji']} {r['alert_level']})")
        print(f"      Days to Cover: {r['days_to_cover']:.1f}")
        print(
            f"      Cost to Borrow: ~{r['cost_to_borrow'] * 100:.1f}%/yr"
            if r["cost_to_borrow"] > 0
            else "      Cost to Borrow: N/A"
        )
        print(f"      5D Return: {r['returns_5d']:+.1f}%  |  1M Return: {r['returns_1m']:+.1f}%")
        print(f"      52W Position: {r['price_position']:.0f}%")
        if r.get("gamma"):
            gamma = r["gamma"]
            imbalance = (
                "CALL HEAVY (upside squeeze potential)"
                if gamma["gamma_ratio"] > 0.1
                else "PUT HEAVY (downside pressure)"
                if gamma["gamma_ratio"] < -0.1
                else "BALANCED"
            )
            print(f"      Gamma OI: {gamma['call_oi']:,} calls / {gamma['put_oi']:,} puts -> {imbalance}")

    print(f"\n{'─' * 70}")
    print(f"TOP SQUEEZE CANDIDATE")
    print(f"{'─' * 70}")
    best = results[0]
    print(f"   {best['ticker']} - Score:{best['squeeze_score']}/100 ({best['alert_emoji']} {best['alert_level']})")
    if best["squeeze_score"] >= 70:
        print(f"   >> HIGH SHORT SQUEEZE POTENTIAL")
        print(f"   Warning: High short interest + momentum = squeeze risk")
    elif best["squeeze_score"] >= 50:
        print(f"   >> MODERATE SHORT SQUEEZE POTENTIAL")
    else:
        print(f"   >> LOW SHORT SQUEEZE POTENTIAL")
    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    main()
