#!/usr/bin/env python3
r"""
Macro Regime Forecast (edge-hunter)
===================================
Generates 3/6-month directional forecasts across macro asset classes:
rates, gold, oil, dollar, equities.

Usage:
    python macro_forecast.py
    python macro_forecast.py --assets TLT GLD SPY
"""

import argparse
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, safe_float

try:
    import yfinance as yf
    import numpy as np
    import pandas as pd
except ImportError:
    print("ERROR: Install dependencies: pip3 install yfinance numpy pandas")
    sys.exit(1)


DEFAULT_ASSETS = {
    "SPY": ("Equities", "S&P 500 - risk-on/risk-off benchmark"),
    "QQQ": ("Tech/Growth", "Nasdaq 100 - growth proxy"),
    "TLT": ("Rates", "20+ Year Treasury - rate direction"),
    "GLD": ("Gold", "Gold - inflation/hedge proxy"),
    "USO": ("Oil", "Crude Oil - inflation/growth proxy"),
    "UUP": ("Dollar", "USD Index - dollar strength"),
    "VIX": ("Volatility", "VIX - fear gauge"),
}


def fetch_macro_data(assets, start_date=None):
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    data = {}
    for ticker in assets:
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not df.empty:
                df = flatten_yf_data(df)
                data[ticker] = df["Close"]
        except Exception:
            pass
    return pd.DataFrame(data) if data else pd.DataFrame()


def calculate_indicators(series):
    if series.empty or len(series) < 60:
        return None
    sma_20 = series.rolling(20).mean()
    sma_60 = series.rolling(60).mean()
    sma_200 = series.rolling(200).mean() if len(series) > 200 else None
    current = series.iloc[-1]
    trend_20 = "ABOVE" if current > sma_20.iloc[-1] else "BELOW"
    trend_60 = "ABOVE" if current > sma_60.iloc[-1] else "BELOW"
    trend_200 = "ABOVE" if (sma_200 is not None and current > sma_200.iloc[-1]) else "N/A"
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi_val = rsi.iloc[-1] if not rsi.isna().all() else 50
    roc_1m = (series.iloc[-1] / series.iloc[-22] - 1) * 100 if len(series) > 22 else 0
    roc_3m = (series.iloc[-1] / series.iloc[-66] - 1) * 100 if len(series) > 66 else 0
    roc_6m = (series.iloc[-1] / series.iloc[-126] - 1) * 100 if len(series) > 126 else 0
    returns = series.pct_change().dropna()
    vol_20 = returns.rolling(20).std().iloc[-1] * np.sqrt(252) * 100 if len(returns) > 20 else 0
    return {
        "current": current,
        "trend_20": trend_20,
        "trend_60": trend_60,
        "trend_200": trend_200,
        "rsi": rsi_val,
        "roc_1m": roc_1m,
        "roc_3m": roc_3m,
        "roc_6m": roc_6m,
        "volatility": vol_20,
    }


def directional_forecast(indicators):
    if not indicators:
        return "INSUFFICIENT DATA", "INSUFFICIENT DATA"
    score = 0
    if indicators["trend_60"] == "ABOVE":
        score += 2
    elif indicators["trend_60"] == "BELOW":
        score -= 2
    if indicators["trend_200"] != "N/A":
        if indicators["trend_200"] == "ABOVE":
            score += 1
        elif indicators["trend_200"] == "BELOW":
            score -= 1
    if indicators["roc_3m"] > 10:
        score += 2
    elif indicators["roc_3m"] > 5:
        score += 1
    elif indicators["roc_3m"] < -10:
        score -= 2
    elif indicators["roc_3m"] < -5:
        score -= 1
    rsi = indicators["rsi"]
    if 40 <= rsi <= 60:
        score += 1
    elif rsi > 75:
        score -= 1
    elif rsi < 30:
        score += 1
    if score >= 3:
        forecast_3m = "BULLISH "
    elif score >= 1:
        forecast_3m = "SLIGHTLY BULLISH"
    elif score <= -3:
        forecast_3m = "BEARISH "
    elif score <= -1:
        forecast_3m = "SLIGHTLY BEARISH"
    else:
        forecast_3m = "NEUTRAL "
    score_6m = score
    if indicators["roc_6m"] > 15:
        score_6m += 1
    elif indicators["roc_6m"] < -15:
        score_6m -= 1
    if score_6m >= 3:
        forecast_6m = "BULLISH "
    elif score_6m >= 1:
        forecast_6m = "SLIGHTLY BULLISH"
    elif score_6m <= -3:
        forecast_6m = "BEARISH "
    elif score_6m <= -1:
        forecast_6m = "SLIGHTLY BEARISH"
    else:
        forecast_6m = "NEUTRAL "
    return forecast_3m, forecast_6m


def identify_macro_theme(indicators):
    themes = []
    if "SPY" in indicators and "TLT" in indicators:
        spy_trend = indicators["SPY"]["trend_60"]
        tlt_trend = indicators["TLT"]["trend_60"]
        if spy_trend == "ABOVE" and tlt_trend == "ABOVE":
            themes.append("FALLING RATES + GROWTH (Goldilocks)")
        elif spy_trend == "ABOVE" and tlt_trend == "BELOW":
            themes.append("REFLATION (rising rates + growth)")
        elif spy_trend == "BELOW" and tlt_trend == "ABOVE":
            themes.append("RISK-OFF (flight to safety)")
        elif spy_trend == "BELOW" and tlt_trend == "BELOW":
            themes.append("STAGFLATION (falling growth + rising rates)")
    if "GLD" in indicators and "USO" in indicators:
        gld_roc = indicators["GLD"]["roc_3m"]
        uso_roc = indicators["USO"]["roc_3m"]
        if gld_roc > 10 and uso_roc > 10:
            themes.append("INFLATION PRESSURE")
        elif gld_roc < -5 and uso_roc < -5:
            themes.append("DISINFLATION")
    if "UUP" in indicators:
        dollar_roc = indicators["UUP"]["roc_3m"]
        if dollar_roc > 5:
            themes.append("DOLLAR STRENGTHENING")
        elif dollar_roc < -5:
            themes.append("DOLLAR WEAKENING")
    if "VIX" in indicators:
        vix = indicators["VIX"]["current"]
        if vix > 25:
            themes.append("HIGH VOL / FEAR")
        elif vix < 15:
            themes.append("LOW VOL / COMPLACENCY")
    return themes


def main():
    parser = argparse.ArgumentParser(
        description="Macro Regime Forecast - 3/6-month directional analysis across asset classes"
    )
    parser.add_argument(
        "--assets", nargs="+", default=list(DEFAULT_ASSETS.keys()), help="Assets to analyze (default: all macro assets)"
    )
    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"MACRO REGIME FORECAST")
    print(f"{'=' * 70}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"  Assets: {', '.join(args.assets)}")

    data = fetch_macro_data(args.assets)
    if data.empty:
        print("\n[ERROR] No data fetched. Check connection and tickers.")
        return

    indicators = {}
    for ticker in args.assets:
        if ticker in data.columns:
            ind = calculate_indicators(data[ticker])
            if ind:
                indicators[ticker] = ind

    themes = identify_macro_theme(indicators)
    print(f"\n{'─' * 70}")
    print(f"DOMINANT MACRO THEMES")
    print(f"{'─' * 70}")
    for theme in themes:
        print(f"  >> {theme}")
    if not themes:
        print("  >> No clear dominant theme - mixed signals")

    print(f"\n{'─' * 70}")
    print(f"ASSET-BY-ASSET ANALYSIS")
    print(f"{'─' * 70}")

    results = []
    for ticker in args.assets:
        if ticker not in indicators:
            continue
        ind = indicators[ticker]
        cat, _desc = DEFAULT_ASSETS.get(ticker, ("Other", ""))
        forecast_3m, forecast_6m = directional_forecast(ind)
        rsi = ind["rsi"]
        if rsi > 70:
            rsi_signal = "OVERBOUGHT"
        elif rsi < 30:
            rsi_signal = "OVERSOLD"
        elif rsi > 60:
            rsi_signal = "BULLISH ZONE"
        elif rsi < 40:
            rsi_signal = "BEARISH ZONE"
        else:
            rsi_signal = "NEUTRAL"
        print(f"\n  {ticker} ({cat})")
        print(f"    Price: ${ind['current']:.2f}")
        print(f"    Trend: {ind['trend_60']} vs 60-day MA")
        print(f"    RSI(14): {rsi:.1f} - {rsi_signal}")
        print(f"    3M ROC: {ind['roc_3m']:+.1f}%")
        print(f"    6M ROC: {ind['roc_6m']:+.1f}%")
        print(f"    Vol: {ind['volatility']:.1f}% annualized")
        print(f"    3M Forecast: {forecast_3m}")
        print(f"    6M Forecast: {forecast_6m}")
        results.append(
            {
                "ticker": ticker,
                "category": cat,
                "forecast_3m": forecast_3m,
                "forecast_6m": forecast_6m,
                "rsi": rsi,
                "trend": ind["trend_60"],
            }
        )

    print(f"\n{'─' * 70}")
    print(f"FORECAST SUMMARY")
    print(f"{'─' * 70}")
    print(f"\n  {'Ticker':8} {'3M Forecast':18} {'6M Forecast':18}")
    print(f"  {'─' * 8} {'─' * 18} {'─' * 18}")
    for r in results:
        print(f"  {r['ticker']:8} {r['forecast_3m']:18} {r['forecast_6m']:18}")
    bullish_count = sum(1 for r in results if "BULLISH" in r["forecast_3m"])
    bearish_count = sum(1 for r in results if "BEARISH" in r["forecast_3m"])
    print(f"\n  Bullish signals: {bullish_count}/{len(results)}")
    print(f"  Bearish signals: {bearish_count}/{len(results)}")
    if bullish_count > bearish_count * 1.5:
        print(f"  >> Overall: RISK-ON BIAS")
    elif bearish_count > bullish_count * 1.5:
        print(f"  >> Overall: RISK-OFF BIAS")
    else:
        print(f"  >> Overall: MIXED - no dominant directional signal")
    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    main()
