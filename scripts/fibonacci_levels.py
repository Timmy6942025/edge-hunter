#!/usr/bin/env python3
"""
Fibonacci Levels Script (Professional Quant)
================================================
- Key Fibonacci retracement levels
- Extension levels
- Support/resistance confluence
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

FIB_RETRACEMENTS = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
FIB_EXTENSIONS = [1.272, 1.382, 1.618, 2.0, 2.618]


def find_swing_highs_lows(data, lookback=50):
    """Find significant swing highs and lows"""
    highs = []
    lows = []

    for i in range(lookback, len(data) - lookback):
        window_high = data["High"].iloc[i - lookback : i + lookback + 1]
        window_low = data["Low"].iloc[i - lookback : i + lookback + 1]

        val_high = float(data["High"].iloc[i])
        val_low = float(data["Low"].iloc[i])

        if val_high == float(window_high.max()):
            highs.append({"index": i, "price": val_high, "date": data.index[i]})

        if val_low == float(window_low.min()):
            lows.append({"index": i, "price": val_low, "date": data.index[i]})

    return highs, lows


def calculate_fib_levels(swing_high, swing_low, direction="UPTREND"):
    """Calculate Fibonacci retracement and extension levels"""
    levels = []

    if direction == "UPTREND":
        start = swing_high
        end = swing_low
    else:
        start = swing_low
        end = swing_high

    diff = start - end

    # Retracement levels
    for fib in FIB_RETRACEMENTS:
        price = start - diff * fib
        levels.append({"type": "Retracement", "fib": fib, "price": price, "direction": direction})

    # Extension levels
    for fib in FIB_EXTENSIONS:
        price = start + diff * (fib - 1)
        levels.append({"type": "Extension", "fib": fib, "price": price, "direction": direction})

    return levels


def main():
    parser = argparse.ArgumentParser(description="Fibonacci Levels Analysis")
    parser.add_argument("ticker", help="Ticker to analyze")
    parser.add_argument("--period", default="6mo", help="Data period")
    parser.add_argument("--lookback", type=int, default=50, help="Swing detection lookback")
    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"FIBONACCI LEVELS ANALYSIS: {args.ticker}")
    print(f"{'=' * 70}")
    print(f"Period: {args.period}")

    data = yf.download(args.ticker, period=args.period, progress=False)
    if data.empty:
        print("❌ No data available")
        return

    data = flatten_yf_data(data)
    current_price = float(data["Close"].iloc[-1])

    print(f"   Current Price: ${current_price:.2f}")

    # Find swing points
    highs, lows = find_swing_highs_lows(data, args.lookback)

    if not highs or not lows:
        print("   ⚠️ Not enough swing points found. Try a longer period or smaller lookback.")
        # Fallback: use overall high/low
        overall_high = float(data["High"].max())
        overall_low = float(data["Low"].min())
        highs = [{"price": overall_high, "date": data["High"].idxmax()}]
        lows = [{"price": overall_low, "date": data["Low"].idxmin()}]
        print(f"   Using overall high/low: ${overall_high:.2f} / ${overall_low:.2f}")

    # Determine trend direction
    recent_high = max(h["price"] for h in highs[-3:]) if len(highs) >= 3 else highs[-1]["price"]
    recent_low = min(low["price"] for low in lows[-3:]) if len(lows) >= 3 else lows[-1]["price"]

    if current_price > (recent_high + recent_low) / 2:
        direction = "UPTREND"
    else:
        direction = "DOWNTREND"

    print(f"\n{'─' * 70}")
    print(f"TREND DIRECTION: {direction}")
    print(f"{'─' * 70}")

    # Calculate Fibonacci levels
    levels = calculate_fib_levels(recent_high, recent_low, direction)

    print(f"\n{'─' * 70}")
    print(f"FIBONACCI RETRACEMENT LEVELS")
    print(f"{'─' * 70}")

    for level in levels:
        if level["type"] == "Retracement":
            dist_pct = ((level["price"] - current_price) / current_price) * 100

            # Mark proximity
            if abs(dist_pct) < 2:
                marker = "◀◀◀ NEAR"
            elif abs(dist_pct) < 5:
                marker = "◀ CLOSE"
            else:
                marker = ""

            print(f"   {level['fib']:.3f}: ${level['price']:.2f} ({dist_pct:+.1f}%) {marker}")

    print(f"\n{'─' * 70}")
    print(f"FIBONACCI EXTENSION LEVELS")
    print(f"{'─' * 70}")

    for level in levels:
        if level["type"] == "Extension":
            dist_pct = ((level["price"] - current_price) / current_price) * 100

            print(f"   {level['fib']:.3f}: ${level['price']:.2f} ({dist_pct:+.1f}%)")

    # Support/resistance confluence
    print(f"\n{'─' * 70}")
    print(f"SUPPORT/RESISTANCE CONFLUENCE")
    print(f"{'─' * 70}")

    # Key levels with confluence
    support_levels = [lvl for lvl in levels if lvl["type"] == "Retracement" and lvl["price"] < current_price]
    resistance_levels = [lvl for lvl in levels if lvl["type"] == "Retracement" and lvl["price"] > current_price]

    if support_levels:
        print(f"\n   🟢 SUPPORT LEVELS:")
        for lvl in sorted(support_levels, key=lambda x: abs(x["price"] - current_price))[:4]:
            strength = "STRONG" if lvl["fib"] in [0.618, 0.382] else ("MODERATE" if lvl["fib"] == 0.5 else "WEAK")
            print(f"      {lvl['fib']:.3f}: ${lvl['price']:.2f} ({strength})")

    if resistance_levels:
        print(f"\n   🔴 RESISTANCE LEVELS:")
        for lvl in sorted(resistance_levels, key=lambda x: abs(x["price"] - current_price))[:4]:
            strength = "STRONG" if lvl["fib"] in [0.618, 0.382] else ("MODERATE" if lvl["fib"] == 0.5 else "WEAK")
            print(f"      {lvl['fib']:.3f}: ${lvl['price']:.2f} ({strength})")

    # Trading zones
    print(f"\n{'─' * 70}")
    print(f"TRADING ZONES")
    print(f"{'─' * 70}")

    # Find the zone price is in
    fib_382 = [lvl["price"] for lvl in levels if lvl["fib"] == 0.382 and lvl["type"] == "Retracement"]
    fib_618 = [lvl["price"] for lvl in levels if lvl["fib"] == 0.618 and lvl["type"] == "Retracement"]

    if fib_382 and fib_618:
        zone_low = min(fib_382[0], fib_618[0])
        zone_high = max(fib_382[0], fib_618[0])

        if zone_low <= current_price <= zone_high:
            print(f"   📍 Price IN Fibonacci Zone (0.382-0.618)")
            print(f"      Zone: ${zone_low:.2f} - ${zone_high:.2f}")
            print(f"      Decision zone - watch for bounce/break")
        elif current_price > zone_high:
            print(f"   📍 Price ABOVE Fibonacci Zone")
            print(f"      Next support: ${zone_high:.2f}")
        else:
            print(f"   📍 Price BELOW Fibonacci Zone")
            print(f"      Next resistance: ${zone_low:.2f}")


if __name__ == "__main__":
    main()
