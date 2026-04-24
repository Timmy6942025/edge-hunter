#!/usr/bin/env python3
"""
Volume Profile Script (Professional Quant)
================================================
- VWAP calculation and analysis
- Volume at price levels
- Point of Control (POC) identification
- Value area calculation
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


def calculate_vwap(data):
    """Calculate Volume Weighted Average Price"""
    typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
    cumulative_tp_volume = (typical_price * data["Volume"]).cumsum()
    cumulative_volume = data["Volume"].cumsum()
    vwap = cumulative_tp_volume / cumulative_volume
    return vwap


def calculate_vwap_bands(vwap, data, multiplier=1.5):
    """Calculate VWAP standard deviation bands"""
    typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
    returns = typical_price.pct_change().dropna()
    std = returns.rolling(20).std().iloc[-1] * vwap.iloc[-1]

    return {
        "upper1": vwap.iloc[-1] + std * multiplier,
        "lower1": vwap.iloc[-1] - std * multiplier,
        "upper2": vwap.iloc[-1] + std * 2 * multiplier,
        "lower2": vwap.iloc[-1] - std * 2 * multiplier,
        "std": std,
    }


def calculate_volume_profile(data, bins=50):
    """Calculate volume at price levels (vectorized - no iterrows)"""
    # Create price bins
    price_min = data["Low"].min()
    price_max = data["High"].max()

    bins_array = np.linspace(price_min, price_max, bins)

    # Vectorized volume profile calculation
    # For each day, distribute volume across 10 price points between Low and High
    n_points = 10
    all_prices = []
    all_volumes = []

    for i in range(len(data)):
        low = data["Low"].iloc[i]
        high = data["High"].iloc[i]
        vol = data["Volume"].iloc[i]
        prices = np.linspace(low, high, n_points)
        vol_per_point = vol / n_points
        all_prices.extend(prices)
        all_volumes.extend([vol_per_point] * n_points)

    all_prices = np.array(all_prices)
    all_volumes = np.array(all_volumes)

    # Use numpy histogram to bin volumes by price
    vol_hist, _ = np.histogram(all_prices, bins=bins_array, weights=all_volumes)
    volume_profile = pd.Series(vol_hist, index=bins_array[:-1])

    # Find Point of Control (POC) - highest volume price
    poc_idx = volume_profile.idxmax()
    poc_volume = volume_profile.max()

    # Calculate Value Area (70% of volume)
    total_volume = volume_profile.sum()
    target_volume = total_volume * 0.70

    sorted_profile = volume_profile.sort_values(ascending=False)
    cumsum = 0
    value_area_prices = []

    for price, vol in sorted_profile.items():
        cumsum += vol
        value_area_prices.append(price)
        if cumsum >= target_volume:
            break

    value_area_low = min(value_area_prices)
    value_area_high = max(value_area_prices)

    return {
        "profile": volume_profile,
        "poc": poc_idx,
        "poc_volume": poc_volume,
        "value_area_low": value_area_low,
        "value_area_high": value_area_high,
        "value_area_volume": cumsum,
    }


def main():
    parser = argparse.ArgumentParser(description="Volume Profile Analysis")
    parser.add_argument("tickers", nargs="+", help="Tickers to analyze")
    parser.add_argument("--period", default="1mo", help="Data period")
    parser.add_argument("--bins", type=int, default=50, help="Volume profile bins")
    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"VOLUME PROFILE ANALYSIS")
    print(f"{'=' * 70}")
    print(f"Period: {args.period}")
    print(f"Price bins: {args.bins}")

    for ticker in args.tickers:
        print(f"\n{'─' * 70}")
        print(f"📊 {ticker}")
        print(f"{'─' * 70}")

        data = yf.download(ticker, period=args.period, progress=False)
        data = flatten_yf_data(data)

        if data.empty:
            print(f"❌ No data for {ticker}")
            continue

        current_price = float(data["Close"].iloc[-1])

        # ========== VWAP ==========
        vwap = calculate_vwap(data)
        bands = calculate_vwap_bands(vwap, data)

        print(f"\n📈 VWAP ANALYSIS")
        print(f"   {'─' * 40}")
        print(f"   VWAP: ${vwap.iloc[-1]:.2f}")
        print(f"   Current Price: ${current_price:.2f}")
        print(f"   Price vs VWAP: {((current_price / vwap.iloc[-1]) - 1) * 100:+.2f}%")

        # VWAP position
        if current_price > vwap.iloc[-1] * 1.01:
            print(f"   📍 Position: ABOVE VWAP (Bullish)")
        elif current_price < vwap.iloc[-1] * 0.99:
            print(f"   📍 Position: BELOW VWAP (Bearish)")
        else:
            print(f"   📍 Position: AT VWAP (Neutral)")

        print(f"\n   📊 VWAP BANDS:")
        print(f"      +1 SD: ${bands['upper1']:.2f} ({((bands['upper1'] / current_price) - 1) * 100:+.2f}%)")
        print(f"      -1 SD: ${bands['lower1']:.2f} ({((bands['lower1'] / current_price) - 1) * 100:+.2f}%)")
        print(f"      +2 SD: ${bands['upper2']:.2f} ({((bands['upper2'] / current_price) - 1) * 100:+.2f}%)")
        print(f"      -2 SD: ${bands['lower2']:.2f} ({((bands['lower2'] / current_price) - 1) * 100:+.2f}%)")

        # ========== VOLUME PROFILE ==========
        vp_data = calculate_volume_profile(data, args.bins)

        print(f"\n📊 VOLUME PROFILE")
        print(f"   {'─' * 40}")

        print(f"   🎯 Point of Control (POC): ${vp_data['poc']:.2f}")
        print(f"      High Volume Zone Price")

        print(f"\n   📍 VALUE AREA (70% of volume):")
        print(f"      Low: ${vp_data['value_area_low']:.2f}")
        print(f"      High: ${vp_data['value_area_high']:.2f}")

        # Current price vs value area
        if current_price < vp_data["value_area_low"]:
            print(f"\n   📍 Price BELOW Value Area (Potential bounce)")
        elif current_price > vp_data["value_area_high"]:
            print(f"\n   📍 Price ABOVE Value Area (Potential pullback)")
        else:
            print(f"\n   📍 Price WITHIN Value Area (Neutral)")

        # Print ASCII volume profile
        print(f"\n   📊 VOLUME PROFILE (ASCII):")
        profile = vp_data["profile"]
        max_vol = profile.max()

        # Normalize for display
        normalized = profile / max_vol

        # Find current price position in profile
        price_range = profile.index

        # Show key levels with volume bars
        print(f"   {'─' * 50}")
        step = len(profile) // 15
        for i in range(0, len(profile), max(1, step)):
            price = profile.index[i]
            vol = normalized.iloc[i]
            bar = "█" * int(vol * 30)

            # Mark POC
            marker = "◀◀◀" if abs(price - vp_data["poc"]) < (price_range[1] - price_range[0]) else ""

            print(f"   ${price:.2f} |{bar}| {marker}")
        print(f"   {'─' * 50}")

        # ========== SHORT-TERM SIGNALS ==========
        print(f"\n📅 RECENT SESSION ANALYSIS")

        # Today's volume vs average
        today_vol = data["Volume"].iloc[-1]
        avg_vol = data["Volume"].rolling(20).mean().iloc[-1]
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1

        print(f"   Today Volume: {vol_ratio:.2f}x 20-day avg")

        if vol_ratio > 2:
            print(f"   ⚠️ HIGH VOLUME day - significant move likely")

        # Price position
        high = data["High"].iloc[-1]
        low = data["Low"].iloc[-1]
        range_pct = ((high - low) / low) * 100

        print(f"   Today Range: {range_pct:.2f}% (${low:.2f} - ${high:.2f})")

        if current_price > vwap.iloc[-1] and current_price > high * 0.95:
            print(f"   🟢 Close near high - bullish intraday")
        elif current_price < vwap.iloc[-1] and current_price < low * 1.05:
            print(f"   🔴 Close near low - bearish intraday")


if __name__ == "__main__":
    main()
