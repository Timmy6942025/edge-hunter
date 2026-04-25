#!/usr/bin/env python3
r"""
Earnings Transcript Analysis (edge-hunter)
==========================================
Fetches and analyzes earnings call structure from yfinance.
Extracts guidance signals, management tone, and key financial metrics.

Usage:
    python earnings_transcript.py NVDA
    python earnings_transcript.py NVDA --quarters 4
    python earnings_transcript.py AAPL MSFT GOOGL
"""

import argparse
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import safe_float

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip3 install yfinance")
    sys.exit(1)


CONFIDENT_WORDS = {
    "strong",
    "confident",
    "record",
    "momentum",
    "significant",
    "accelerating",
    "dramatically",
    "clearly",
    "robust",
    "solid",
    "exceptional",
    "outstanding",
    "exceeded",
    "beat",
    "growing",
    "demand visibility",
    "compelling",
    "substantial",
    "meaningfully",
}

HEDGING_WORDS = {
    "monitor",
    "cautiously",
    "challenging",
    "uncertain",
    "volatile",
    "difficult",
    "environment",
    "broadly",
    "somewhat",
    "moderating",
    "mixed",
    "caveats",
    "subject to",
    "careful",
    "carefully",
    "depends",
    "early to say",
    "premature",
    "remain focused",
}


def fetch_earnings_data(ticker, quarters=4):
    """Fetch earnings data from yfinance info for recent quarters."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return info


def analyze_management_tone(text):
    """Score management tone by counting confident vs hedging phrases."""
    if not text:
        return 0, "NEUTRAL", 0, 0

    text_lower = text.lower()
    confident_count = sum(1 for word in CONFIDENT_WORDS if word in text_lower)
    hedging_count = sum(1 for phrase in HEDGING_WORDS if phrase in text_lower)
    net_score = confident_count - hedging_count

    if net_score >= 3:
        tone = "CONFIDENT"
    elif net_score >= 1:
        tone = "SLIGHTLY CONFIDENT"
    elif net_score <= -3:
        tone = "CAUTIOUS"
    elif net_score <= -1:
        tone = "SLIGHTLY CAUTIOUS"
    else:
        tone = "NEUTRAL"

    return net_score, tone, confident_count, hedging_count


def extract_guidance_signals(info):
    """Extract guidance-related signals from yfinance info."""
    signals = []

    rev_growth = info.get("revenueGrowth")
    if rev_growth is not None:
        if rev_growth >= 0.20:
            signals.append(("revenue_growth", "ACCELERATING", f"{rev_growth * 100:.1f}% YoY"))
        elif rev_growth >= 0.10:
            signals.append(("revenue_growth", "SOLID", f"{rev_growth * 100:.1f}% YoY"))
        elif rev_growth >= 0:
            signals.append(("revenue_growth", "MODERATE", f"{rev_growth * 100:.1f}% YoY"))
        else:
            signals.append(("revenue_growth", "CONTRACTING", f"{rev_growth * 100:.1f}% YoY"))

    ern_growth = info.get("earningsGrowth")
    if ern_growth is not None:
        if ern_growth >= 0.20:
            signals.append(("earnings_growth", "ACCELERATING", f"{ern_growth * 100:.1f}% YoY"))
        elif ern_growth >= 0.10:
            signals.append(("earnings_growth", "SOLID", f"{ern_growth * 100:.1f}% YoY"))
        elif ern_growth >= 0:
            signals.append(("earnings_growth", "MODERATE", f"{ern_growth * 100:.1f}% YoY"))
        else:
            signals.append(("earnings_growth", "DECLINING", f"{ern_growth * 100:.1f}% YoY"))

    gross_margin = info.get("grossMargins")
    if gross_margin is not None:
        if gross_margin >= 0.50:
            signals.append(("gross_margin", "HIGH", f"{gross_margin * 100:.1f}%"))
        elif gross_margin >= 0.35:
            signals.append(("gross_margin", "SOLID", f"{gross_margin * 100:.1f}%"))
        elif gross_margin >= 0.20:
            signals.append(("gross_margin", "MODERATE", f"{gross_margin * 100:.1f}%"))
        else:
            signals.append(("gross_margin", "LOW", f"{gross_margin * 100:.1f}%"))

    fcf = info.get("freeCashflow")
    net_income = info.get("netIncomeToCommon")
    if fcf is not None and net_income is not None and net_income > 0:
        if fcf > net_income:
            signals.append(("fcf_quality", "HIGH", f"FCF ${fcf / 1e9:.1f}B > NI"))
        elif fcf > 0:
            signals.append(("fcf_quality", "OK", f"FCF ${fcf / 1e9:.1f}B"))
        else:
            signals.append(("fcf_quality", "WEAK", f"FCF ${fcf / 1e9:.1f}B"))

    return signals


def detect_red_flags(info):
    """Detect earnings manipulation or quality red flags."""
    flags = []

    sbc = info.get("stockBasedCompensation")
    revenue = info.get("totalRevenue")
    if sbc is not None and revenue is not None and revenue > 0:
        sbc_pct = sbc / revenue
        if sbc_pct > 0.15:
            flags.append(("SBC_high", "HIGH", f"SBC {sbc_pct * 100:.1f}% of revenue"))
        elif sbc_pct > 0.08:
            flags.append(("SBC_elevated", "WATCH", f"SBC {sbc_pct * 100:.1f}% of revenue"))

    debt_equity = info.get("debtToEquity")
    if debt_equity is not None:
        if debt_equity > 2.0:
            flags.append(("debt_high", "HIGH", f"D/E: {debt_equity:.1f}x"))
        elif debt_equity > 1.0:
            flags.append(("debt_elevated", "WATCH", f"D/E: {debt_equity:.1f}x"))

    current_ratio = info.get("currentRatio")
    if current_ratio is not None:
        if current_ratio < 0.8:
            flags.append(("liquidity_weak", "HIGH", f"Current ratio: {current_ratio:.2f}"))
        elif current_ratio < 1.0:
            flags.append(("liquidity_tight", "WATCH", f"Current ratio: {current_ratio:.2f}"))

    profit_margin = info.get("profitMargins")
    if profit_margin is not None and profit_margin < 0:
        flags.append(("loss", "BEARISH", "Unprofitable - verify growth path"))

    return flags


def analyze_earnings(ticker, quarters=4):
    """Main earnings analysis for a ticker."""
    stock = yf.Ticker(ticker)
    info = stock.info

    print(f"\n{'=' * 70}")
    print(f"EARNINGS ANALYSIS: {ticker}")
    print(f"{'=' * 70}")

    company_name = info.get("longName") or info.get("shortName") or ticker
    print(f"\n  Company: {company_name}")
    print(f"  Sector: {info.get('sector', 'N/A')} / {info.get('industry', 'N/A')}")

    print(f"\n{'─' * 70}")
    print(f"REVENUE & GROWTH")
    print(f"{'─' * 70}")

    revenue = safe_float(info.get("totalRevenue"))
    rev_growth = info.get("revenueGrowth")
    if revenue > 0:
        print(f"  Revenue: ${revenue / 1e9:.2f}B")
        print(f"  YoY Growth: {rev_growth * 100:.1f}%" if rev_growth else "  YoY Growth: N/A")

    print(f"\n{'─' * 70}")
    print(f"EPS ANALYSIS")
    print(f"{'─' * 70}")

    trailing_eps = safe_float(info.get("trailingEps"))
    forward_eps = safe_float(info.get("forwardEps"))
    current_price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))

    print(f"  Trailing EPS: ${trailing_eps:.2f}" if trailing_eps else "  Trailing EPS: N/A")
    print(f"  Forward EPS: ${forward_eps:.2f}" if forward_eps else "  Forward EPS: N/A")

    if trailing_eps > 0 and forward_eps > 0:
        growth = (forward_eps / trailing_eps - 1) * 100
        print(f"  1-Year EPS Growth: {growth:.1f}%")
        if current_price > 0 and trailing_eps > 0:
            print(f"  Trailing P/E: {current_price / trailing_eps:.1f}x")
        if current_price > 0 and forward_eps > 0:
            print(f"  Forward P/E: {current_price / forward_eps:.1f}x")
        forward_pe = info.get("forwardPE")
        if forward_pe and rev_growth:
            peg = forward_pe / (rev_growth * 100)
            if peg < 1.0:
                print(f"  PEG Ratio: {peg:.2f} (cheap)")
            elif peg < 2.0:
                print(f"  PEG Ratio: {peg:.2f} (fair)")
            else:
                print(f"  PEG Ratio: {peg:.2f} (expensive)")

    print(f"\n{'─' * 70}")
    print(f"GUIDANCE SIGNALS")
    print(f"{'─' * 70}")

    signals = extract_guidance_signals(info)
    if signals:
        for sig_type, signal, detail in signals:
            if signal in ("ACCELERATING", "HIGH", "STRONG"):
                emoji = "🟢"
            elif signal in ("SOLID", "OK"):
                emoji = "🟡"
            else:
                emoji = "⚪"
            print(f"  {emoji} {sig_type.upper():25} {signal:15} {detail}")
    else:
        print("  No strong guidance signals detected")

    print(f"\n{'─' * 70}")
    print(f"MANAGEMENT TONE")
    print(f"{'─' * 70}")

    tone_text = " ".join(
        [
            str(info.get("longBusinessSummary", "") or ""),
            str(info.get("strategy", "") or ""),
        ]
    )

    net_score, tone, confident, hedging = analyze_management_tone(tone_text)
    print(f"  Tone Assessment: {tone}")
    print(f"  Confident phrases: {confident} | Hedging phrases: {hedging}")
    print(f"  Net Tone Score: {net_score:+d}")

    if confident > hedging:
        print(f"  -> Management appears {tone.lower()} - positive signal")
    elif hedging > confident:
        print(f"  -> Management appears {tone.lower()} - caution signal")
    else:
        print(f"  -> Management tone is balanced")

    print(f"\n{'─' * 70}")
    print(f"QUALITY FLAGS & RED FLAGS")
    print(f"{'─' * 70}")

    flags = detect_red_flags(info)
    if flags:
        for flag_type, severity, detail in flags:
            if severity == "HIGH":
                emoji = "🔴"
            elif severity == "WATCH":
                emoji = "🟡"
            else:
                emoji = "⚪"
            print(f"  {emoji} {flag_type.upper():25} {severity:8} {detail}")
    else:
        print("  ✅ No major quality red flags detected")

    print(f"\n{'─' * 70}")
    print(f"VALUATION SUMMARY")
    print(f"{'─' * 70}")

    target = info.get("targetMeanPrice")
    if current_price > 0 and target > 0:
        upside = (target / current_price - 1) * 100
        print(f"  Current Price: ${current_price:.2f}")
        print(f"  Target Price:  ${target:.2f}")
        print(f"  Upside:        {upside:+.1f}%")
        if upside > 20:
            print(f"  -> Analyst consensus: BULLISH ({upside:.0f}% upside)")
        elif upside > 5:
            print(f"  -> Analyst consensus: MODERATE BULL ({upside:.0f}% upside)")
        elif upside > -5:
            print(f"  -> Analyst consensus: NEUTRAL")
        else:
            print(f"  -> Analyst consensus: BEARISH ({upside:.0f}% downside)")

    print(f"\n{'=' * 70}\n")


def main():
    parser = argparse.ArgumentParser(description="Earnings Transcript Analysis - guidance, tone, quality flags")
    parser.add_argument("tickers", nargs="+", help="Stock tickers (e.g., NVDA AAPL MSFT)")
    parser.add_argument("--quarters", type=int, default=4, help="Number of quarters to analyze (default: 4)")
    args = parser.parse_args()

    for ticker in args.tickers:
        analyze_earnings(ticker.upper(), args.quarters)


if __name__ == "__main__":
    main()
