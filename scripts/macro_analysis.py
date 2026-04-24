#!/usr/bin/env python3
"""
Macro Economic Analysis
Fetches key macro indicators that affect stock prices (Free, no API key)
Uses yfinance for ETFs that track macro indicators
"""

import yfinance as yf
import pandas as pd
import numpy as np
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import extract_price_data
from datetime import datetime, timedelta


def analyze_macro_environment(ticker="SPY"):
    """
    Analyze macro environment using free ETF proxies:
    - TLT: 20+ Year Treasury (rates proxy)
    - GLD: Gold (inflation hedge)
    - UUP: US Dollar (strength proxy)
    - VIX: Volatility index
    - HYG: High Yield Bonds (risk appetite)
    """
    today = datetime.now()
    one_year_ago = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    print(f"\n{'=' * 70}")
    print(f"MACRO ECONOMIC ANALYSIS (as of {today_str})")
    print(f"{'=' * 70}")

    # VIX - Fear Index
    print(f"\nVOLATILITY REGIME (VIX):")
    try:
        vix = extract_price_data(yf.download("^VIX", start=one_year_ago, end=today_str, progress=False), "Close")
        current_vix = float(vix.iloc[-1])
        avg_vix = float(vix.mean())

        print(f"  Current VIX: {current_vix:.1f}")
        print(f"  1-Year Average: {avg_vix:.1f}")

        if current_vix < 15:
            regime = "VERY LOW FEAR - Complacent market, potential for volatility expansion"
            rating = "RISK-ON"
        elif current_vix < 20:
            regime = "LOW FEAR - Normal market conditions"
            rating = "NEUTRAL"
        elif current_vix < 30:
            regime = "ELEVATED FEAR - Market under stress"
            rating = "RISK-OFF"
        else:
            regime = "EXTREME FEAR - Panic/collapsing market"
            rating = "DEFENSIVE"

        print(f"  Regime: {regime}")
        print(f"  Rating: {rating}")
    except Exception as e:
        print(f"  VIX error: {e}")
        rating = "UNKNOWN"

    # Treasury Rates (TLT proxy)
    print(f"\nINTEREST RATE ENVIRONMENT (TLT - 20Y Treasury):")
    try:
        tlt = extract_price_data(yf.download("TLT", start=one_year_ago, end=today_str, progress=False), "Close")
        tlt_returns = tlt.pct_change().dropna()

        # Bond prices DOWN = rates UP (negative correlation)
        tlt_1m = float(tlt.pct_change(20).iloc[-1] * 100)
        tlt_3m = float(tlt.pct_change(60).iloc[-1] * 100)

        print(f"  TLT 1-Month Change: {tlt_1m:+.2f}%")
        print(f"  TLT 3-Month Change: {tlt_3m:+.2f}%")

        if tlt_1m < -5:
            rate_regime = "RATES RISING (TLT falling) - Headwind for growth stocks"
            impact = "NEGATIVE for high-multiple stocks like AMZN, TSLA"
        elif tlt_1m > 5:
            rate_regime = "RATES FALLING (TLT rising) - Tailwind for growth stocks"
            impact = "POSITIVE for high-multiple stocks"
        else:
            rate_regime = "RATES STABLE - Neutral for most stocks"
            impact = "Neutral"

        print(f"  Regime: {rate_regime}")
        print(f"  Impact: {impact}")
    except Exception as e:
        print(f"  TLT error: {e}")

    # Dollar Strength (UUP)
    print(f"\nDOLLAR STRENGTH (UUP):")
    try:
        uup = extract_price_data(yf.download("UUP", start=one_year_ago, end=today_str, progress=False), "Close")
        uup_3m = float(uup.pct_change(60).iloc[-1] * 100)

        print(f"  UUP 3-Month Change: {uup_3m:+.2f}%")

        if uup_3m > 3:
            dollar = "DOLLAR STRONG - Headwind for exporters, multinationals"
        elif uup_3m < -3:
            dollar = "DOLLAR WEAK - Tailwind for exporters, multinationals"
        else:
            dollar = "DOLLAR NEUTRAL - No significant impact"

        print(f"  Assessment: {dollar}")
    except Exception as e:
        print(f"  UUP error: {e}")

    # Gold (Inflation Hedge)
    print(f"\nINFLATION HEDGE (GLD - Gold):")
    try:
        gld = extract_price_data(yf.download("GLD", start=one_year_ago, end=today_str, progress=False), "Close")
        gld_3m = float(gld.pct_change(60).iloc[-1] * 100)

        print(f"  GLD 3-Month Change: {gld_3m:+.2f}%")

        if gld_3m > 5:
            inflation = "GOLD RISING - Inflation concerns or market fear"
        elif gld_3m < -5:
            inflation = "GOLD FALLING - Disinflation or falling fear"
        else:
            inflation = "GOLD NEUTRAL - Mixed signals"

        print(f"  Signal: {inflation}")
    except Exception as e:
        print(f"  GLD error: {e}")

    # Credit Risk (HYG - High Yield Bonds)
    print(f"\nCREDIT RISK (HYG - High Yield Bonds):")
    try:
        hyg = extract_price_data(yf.download("HYG", start=one_year_ago, end=today_str, progress=False), "Close")
        hyg_3m = float(hyg.pct_change(60).iloc[-1] * 100)

        print(f"  HYG 3-Month Change: {hyg_3m:+.2f}%")

        if hyg_3m > 3:
            credit = "CREDIT EXPANSION - Risk appetite high, bulls in control"
        elif hyg_3m < -3:
            credit = "CREDIT CONTRACTION - Risk aversion, bears emerging"
        else:
            credit = "CREDIT NEUTRAL - Mixed risk appetite"

        print(f"  Assessment: {credit}")
    except Exception as e:
        print(f"  HYG error: {e}")

    # Correlation Analysis
    print(f"\nINTER-MARKET CORRELATIONS (Last 60 Days):")
    try:
        tickers = ["SPY", "TLT", "GLD", "UUP", "^VIX"]
        data = extract_price_data(yf.download(tickers, start=one_year_ago, end=today_str, progress=False), "Close")

        if isinstance(data, pd.DataFrame):
            returns = data.pct_change().dropna()
            spy_returns = returns["SPY"]

            print(f"  SPY vs TLT (rates): {spy_returns.corr(returns['TLT']):.3f} (expect negative)")
            print(f"  SPY vs GLD (inflation): {spy_returns.corr(returns['GLD']):.3f}")
            print(f"  SPY vs UUP (dollar): {spy_returns.corr(returns['UUP']):.3f} (expect negative)")
            print(f"  SPY vs VIX (fear): {spy_returns.corr(returns['^VIX']):.3f} (expect negative)")
    except Exception as e:
        print(f"  Correlation error: {e}")

    # Final Macro Rating
    print(f"\n{'=' * 70}")
    print(f"MACRO RATING FOR EQUITIES:")

    score = 0
    if rating == "RISK-ON":
        score += 2
    elif rating == "NEUTRAL":
        score += 1
    elif rating == "RISK-OFF":
        score -= 1
    elif rating == "DEFENSIVE":
        score -= 2

    if "rate_regime" in locals() and "FALLING" in rate_regime:
        score += 1
    elif "rate_regime" in locals() and "RISING" in rate_regime:
        score -= 1

    if score >= 2:
        macro_rating = "VERY BULLISH - All macro factors aligned"
    elif score == 1:
        macro_rating = "BULLISH - Most macro factors supportive"
    elif score == 0:
        macro_rating = "NEUTRAL - Mixed macro signals"
    elif score == -1:
        macro_rating = "BEARISH - Most macro factors headwinds"
    else:
        macro_rating = "VERY BEARISH - All macro factors negative"

    print(f"  {macro_rating}")
    print(f"{'=' * 70}\n")

    return macro_rating


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Macro economic analysis (free, no API key)")
    parser.add_argument("--ticker", default="SPY", help="Reference ticker for macro context")
    args = parser.parse_args()
    analyze_macro_environment(args.ticker)
