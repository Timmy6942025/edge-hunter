#!/usr/bin/env python3
"""
Technical Alerts Script (Professional Quant)
================================================
- Breakout/breakdown detection
- Support/resistance signals
- Volume spike alerts
- Pattern recognition
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


def detect_breakouts(data, lookback=20):
    """Detect price breakouts from consolidation"""
    signals = []

    current_price = float(data["Close"].iloc[-1])
    current_volume = float(data["Volume"].iloc[-1])

    # Calculate recent range
    high_20 = float(data["High"].tail(lookback).max())
    low_20 = float(data["Low"].tail(lookback).min())
    range_20 = high_20 - low_20
    avg_volume = float(data["Volume"].tail(lookback).mean())

    # Detect breakouts
    if current_price > high_20:
        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        signals.append(
            {
                "type": "BREAKOUT",
                "direction": "BULLISH",
                "price": current_price,
                "level": high_20,
                "volume_ratio": vol_ratio,
                "strength": "STRONG" if vol_ratio > 1.5 else "MODERATE",
            }
        )

    # Detect breakdowns
    if current_price < low_20:
        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        signals.append(
            {
                "type": "BREAKDOWN",
                "direction": "BEARISH",
                "price": current_price,
                "level": low_20,
                "volume_ratio": vol_ratio,
                "strength": "STRONG" if vol_ratio > 1.5 else "MODERATE",
            }
        )

    return signals


def detect_support_resistance(data, window=20):
    """Detect support and resistance levels"""
    levels = []

    for i in range(window, len(data) - window):
        # Check if this is a local high (resistance)
        if data["High"].iloc[i] == data["High"].iloc[i - window : i + window + 1].max():
            levels.append({"price": float(data["High"].iloc[i]), "type": "RESISTANCE", "touches": 1})
        # Check if this is a local low (support)
        if data["Low"].iloc[i] == data["Low"].iloc[i - window : i + window + 1].min():
            levels.append({"price": float(data["Low"].iloc[i]), "type": "SUPPORT", "touches": 1})

    # Merge nearby levels
    if not levels:
        return []

    merged = []
    levels.sort(key=lambda x: x["price"])
    current = levels[0].copy()

    for level in levels[1:]:
        if abs(level["price"] - current["price"]) / current["price"] < 0.02:  # Within 2%
            current["touches"] += level["touches"]
        else:
            merged.append(current)
            current = level.copy()
    merged.append(current)

    return merged


def detect_volume_spikes(data, threshold=2.0, window=20):
    """Detect volume spikes"""
    avg_volume = data["Volume"].rolling(window).mean()
    current_volume = float(data["Volume"].iloc[-1])
    avg = float(avg_volume.iloc[-1]) if not avg_volume.empty else 1

    if avg > 0 and current_volume > avg * threshold:
        return {"detected": True, "ratio": current_volume / avg, "volume": current_volume, "average": avg}
    return {"detected": False}


def calculate_rsi(data, period=14):
    """Calculate RSI"""
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1]) if not rsi.empty else 50


def main():
    parser = argparse.ArgumentParser(description="Technical Alerts")
    parser.add_argument("ticker", help="Ticker to analyze")
    parser.add_argument("--period", default="3mo", help="Data period")
    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"TECHNICAL ALERTS: {args.ticker}")
    print(f"{'=' * 70}")
    print(f"Period: {args.period}")

    data = yf.download(args.ticker, period=args.period, progress=False)
    if data.empty:
        print("❌ No data available")
        return

    data = flatten_yf_data(data)
    current_price = float(data["Close"].iloc[-1])

    print(f"\n   Current Price: ${current_price:.2f}")

    # ========== BREAKOUT/BREAKDOWN DETECTION ==========
    breakouts = detect_breakouts(data)

    print(f"\n{'─' * 70}")
    print(f"BREAKOUT/BREAKDOWN DETECTION")
    print(f"{'─' * 70}")

    if breakouts:
        for signal in breakouts:
            if signal["direction"] == "BULLISH":
                print(f"   🟢 BREAKOUT: Price above ${signal['level']:.2f}")
            else:
                print(f"   🔴 BREAKDOWN: Price below ${signal['level']:.2f}")
            print(f"      Volume: {signal['volume_ratio']:.1f}x average ({signal['strength']})")
    else:
        print(f"   ⚪ No breakout/breakdown detected")
        high_20 = float(data["High"].tail(20).max())
        low_20 = float(data["Low"].tail(20).min())
        dist_to_high = ((high_20 - current_price) / current_price) * 100
        dist_to_low = ((current_price - low_20) / current_price) * 100
        print(f"      Resistance: ${high_20:.2f} ({dist_to_high:.1f}% above)")
        print(f"      Support: ${low_20:.2f} ({dist_to_low:.1f}% below)")

    # ========== SUPPORT/RESISTANCE ==========
    sr_levels = detect_support_resistance(data)

    print(f"\n{'─' * 70}")
    print(f"SUPPORT/RESISTANCE LEVELS")
    print(f"{'─' * 70}")

    if sr_levels:
        for level in sorted(sr_levels, key=lambda x: abs(x["price"] - current_price))[:8]:
            if level["type"] == "RESISTANCE":
                emoji = "🔴"
                dist = ((level["price"] - current_price) / current_price) * 100
                label = f"+{dist:.1f}%"
            else:
                emoji = "🟢"
                dist = ((current_price - level["price"]) / current_price) * 100
                label = f"-{dist:.1f}%"

            print(f"   {emoji} {level['type']}: ${level['price']:.2f} ({label}) [{level['touches']} touches]")
    else:
        print(f"   ⚪ No significant levels detected")

    # ========== VOLUME ALERTS ==========
    vol_spike = detect_volume_spikes(data)

    print(f"\n{'─' * 70}")
    print(f"VOLUME ALERTS")
    print(f"{'─' * 70}")

    if vol_spike["detected"]:
        print(f"   ⚠️ VOLUME SPIKE: {vol_spike['ratio']:.1f}x average")
        print(f"      Volume: {vol_spike['volume']:,.0f}")
        print(f"      20d Average: {vol_spike['average']:,.0f}")
    else:
        avg_vol = float(data["Volume"].rolling(20).mean().iloc[-1])
        cur_vol = float(data["Volume"].iloc[-1])
        ratio = cur_vol / avg_vol if avg_vol > 0 else 1
        print(f"   ⚪ Normal volume: {ratio:.1f}x average")

    # ========== RSI ALERT ==========
    rsi = calculate_rsi(data)

    print(f"\n{'─' * 70}")
    print(f"RSI ALERT")
    print(f"{'─' * 70}")

    print(f"   RSI(14): {rsi:.1f}")

    if rsi > 70:
        print(f"   🔴 OVERBOUGHT - Potential pullback")
    elif rsi > 60:
        print(f"   🟡 ELEVATED RSI - Watch for divergence")
    elif rsi < 30:
        print(f"   🟢 OVERSOLD - Potential bounce")
    elif rsi < 40:
        print(f"   🟡 LOW RSI - Watch for reversal signals")
    else:
        print(f"   ✅ NORMAL RSI range")

    # ========== COMPOSITE ALERT ==========
    print(f"\n{'─' * 70}")
    print(f"ALERT SUMMARY")
    print(f"{'─' * 70}")

    alert_count = 0

    for signal in breakouts:
        if signal["direction"] == "BULLISH":
            print(f"   🟢 BULLISH BREAKOUT")
        else:
            print(f"   🔴 BEARISH BREAKDOWN")
        alert_count += 1

    if vol_spike["detected"]:
        print(f"   ⚠️ Volume spike ({vol_spike['ratio']:.1f}x)")
        alert_count += 1

    if rsi > 70 or rsi < 30:
        direction = "OVERBOUGHT" if rsi > 70 else "OVERSOLD"
        print(f"   📊 RSI {direction} ({rsi:.1f})")
        alert_count += 1

    if alert_count == 0:
        print(f"   ✅ No active alerts - price in normal range")
    else:
        print(f"\n   Total alerts: {alert_count}")


if __name__ == "__main__":
    main()
