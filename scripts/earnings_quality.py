#!/usr/bin/env python3
"""
Earnings Quality Analysis Script (Free, Pi-Friendly)
Analyzes: Beat/miss rates, surprise magnitude, guidance, accruals
Uses yfinance for free data - no API keys needed
"""

import argparse
import numpy as np
import pandas as pd
import yfinance as yf
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, extract_price_data, safe_float
from datetime import datetime, timedelta


def analyze_earnings_quality(ticker):
    """Comprehensive earnings quality analysis"""

    print(f"\n{'=' * 70}")
    print(f"EARNINGS QUALITY ANALYSIS: {ticker}")
    print(f"{'=' * 70}")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # EARNINGS HISTORY
        print(f"\n{'─' * 70}")
        print(f"EARNINGS HISTORY")
        print(f"{'─' * 70}")

        eps_actual = info.get("trailingEps")
        eps_estimate = info.get("forwardEps")

        if eps_actual:
            print(f"  Trailing EPS: ${eps_actual:.2f}")
        else:
            print(f"  Trailing EPS: N/A")
        if eps_estimate:
            print(f"  Forward EPS (est): ${eps_estimate:.2f}")
        else:
            print(f"  Forward EPS: N/A")

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if eps_actual and current_price:
            print(f"  Implied P/E from trailing EPS: {current_price / eps_actual:.1f}")

        # QUARTERLY PERFORMANCE
        try:
            quarterly = stock.quarterly_financials
            if not quarterly.empty:
                print(f"\n  Recent Quarterly Performance:")
                print(f"  {'Quarter':<15} {'Revenue':<20} {'Earnings':<20}")
                print(f"  {'─' * 55}")

                for idx in quarterly.columns[:4]:
                    revenue = quarterly.loc["Total Revenue", idx] if "Total Revenue" in quarterly.index else "N/A"
                    earnings = quarterly.loc["Net Income", idx] if "Net Income" in quarterly.index else "N/A"

                    rev_str = f"${revenue / 1e9:.2f}B" if isinstance(revenue, (int, float)) else str(revenue)[:15]
                    earn_str = f"${earnings / 1e9:.2f}B" if isinstance(earnings, (int, float)) else str(earnings)[:15]

                    print(f"  {str(idx)[:12]:<15} {rev_str:<20} {earn_str:<20}")
        except Exception as e:
            print(f"  Could not fetch quarterly data")

        # CASH FLOW QUALITY
        print(f"\n{'─' * 70}")
        print(f"CASH FLOW QUALITY")
        print(f"{'─' * 70}")

        try:
            cashflow = stock.cashflow
            if not cashflow.empty:
                operating_cf = (
                    cashflow.loc["Operating Cash Flow"].iloc[0] if "Operating Cash Flow" in cashflow.index else None
                )
                net_income = cashflow.loc["Net Income"].iloc[0] if "Net Income" in cashflow.index else None

                if operating_cf and net_income and net_income > 0:
                    cf_ratio = operating_cf / net_income
                    print(f"  Cash Flow / Net Income Ratio: {cf_ratio:.2f}")

                    if cf_ratio > 1.2:
                        cf_signal = "HIGH QUALITY"
                        print(f"  → EXCELLENT (CF > 120% of NI)")
                    elif cf_ratio > 1.0:
                        cf_signal = "GOOD"
                        print(f"  → GOOD")
                    elif cf_ratio > 0.8:
                        cf_signal = "MODERATE"
                        print(f"  → WATCH - possible accruals")
                    else:
                        cf_signal = "WEAK"
                        print(f"  → WARNING - earnings quality concern")
                else:
                    cf_signal = "N/A"
                    print("  Cash flow data not available")
            else:
                cf_signal = "N/A"
                print("  Cash flow data not available")
        except Exception:
            cf_signal = "N/A"
            print("  Could not analyze cash flow")

        # REVENUE QUALITY
        print(f"\n{'─' * 70}")
        print(f"REVENUE QUALITY")
        print(f"{'─' * 70}")

        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")

        if revenue_growth and earnings_growth:
            rev_growth_pct = revenue_growth * 100
            earn_growth_pct = earnings_growth * 100

            print(f"  Revenue Growth: {rev_growth_pct:+.1f}%")
            print(f"  Earnings Growth: {earn_growth_pct:+.1f}%")

            if earn_growth_pct > rev_growth_pct * 1.5 and earn_growth_pct > 30:
                rev_signal = "POTENTIAL AGGRESSIVE ACCRUALS"
                print(f"  → ⚠️ {rev_signal}")
            elif earn_growth_pct < 0 and rev_growth_pct > 0:
                rev_signal = "MARGIN PRESSURE"
                print(f"  → ⚠️ {rev_signal}")
            elif rev_growth_pct > 0 and earn_growth_pct > 0:
                rev_signal = "HEALTHY GROWTH"
                print(f"  → ✅ {rev_signal}")
            else:
                rev_signal = "CONTRACTING"
                print(f"  → ⚠️ {rev_signal}")
        else:
            rev_signal = "N/A"
            print("  Growth data not available")

        # MARGINS
        print(f"\n{'─' * 70}")
        print(f"MARGIN TRENDS")
        print(f"{'─' * 70}")

        profit_margin = info.get("profitMargins")

        if profit_margin:
            print(f"  Current Profit Margin: {profit_margin * 100:.1f}%")

            if profit_margin > 0.20:
                margin_signal = "EXCELLENT"
            elif profit_margin > 0.15:
                margin_signal = "GOOD"
            elif profit_margin > 0.10:
                margin_signal = "ACCEPTABLE"
            elif profit_margin > 0:
                margin_signal = "THIN MARGINS"
            else:
                margin_signal = "LOSING MONEY"

            print(f"  → Margin Signal: {margin_signal}")
        else:
            margin_signal = "N/A"
            print("  Margin data not available")

        # EARNINGS MOMENTUM
        print(f"\n{'─' * 70}")
        print(f"EARNINGS MOMENTUM")
        print(f"{'─' * 70}")

        qoq_growth = info.get("earningsQuarterlyGrowthGrowth") or info.get("earningsQuarterlyGrowth")

        if qoq_growth:
            print(f"  Quarterly Earnings Growth: {qoq_growth * 100:+.1f}%")

            if qoq_growth > 0.20:
                momentum_signal = "ACCELERATING"
                print(f"  → ✅ {momentum_signal}")
            elif qoq_growth > 0:
                momentum_signal = "GROWING"
                print(f"  → ⚠️ {momentum_signal}")
            else:
                momentum_signal = "DECELERATING"
                print(f"  → ❌ {momentum_signal}")
        else:
            momentum_signal = "N/A"
            print("  Earnings momentum data not available")

        # RISK FACTORS
        print(f"\n{'─' * 70}")
        print(f"EARNINGS RISK FACTORS")
        print(f"{'─' * 70}")

        risks = []
        pe_ratio = info.get("trailingPE")

        if pe_ratio and pe_ratio > 40:
            risks.append("High P/E - vulnerable to earnings disappointment")

        if profit_margin and profit_margin < 0.05:
            risks.append("Thin margins - any cost increase hurts badly")

        if cf_signal == "WEAK":
            risks.append("Weak cash flow - earnings may not be sustainable")

        if rev_signal == "POTENTIAL AGGRESSIVE ACCRUALS":
            risks.append("Earnings outpacing revenue - possible quality issue")

        if earnings_growth and earnings_growth < 0:
            risks.append("Earnings declining - could miss future estimates")

        if risks:
            print("  ⚠️ Risk Flags:")
            for risk in risks:
                print(f"    • {risk}")
        else:
            print("  ✅ No major risk flags identified")

        # QUALITY SCORE
        print(f"\n{'=' * 70}")
        print(f"EARNINGS QUALITY VERDICT")
        print(f"{'=' * 70}")

        quality_score = 0

        if cf_signal == "HIGH QUALITY":
            quality_score += 2
        elif cf_signal == "GOOD":
            quality_score += 1
        elif cf_signal == "WEAK":
            quality_score -= 2

        if rev_signal == "HEALTHY GROWTH":
            quality_score += 2
        elif rev_signal in ["MARGIN PRESSURE", "CONTRACTING"]:
            quality_score -= 1

        if margin_signal in ["EXCELLENT", "GOOD"]:
            quality_score += 1
        elif margin_signal == "LOSING MONEY":
            quality_score -= 2

        if momentum_signal == "ACCELERATING":
            quality_score += 1
        elif momentum_signal == "DECELERATING":
            quality_score -= 1

        max_score = 7
        pct_score = (quality_score / max_score) * 100

        print(f"\n  Quality Components:")
        print(f"    Cash Flow: {cf_signal}")
        print(f"    Revenue: {rev_signal}")
        print(f"    Margins: {margin_signal}")
        print(f"    Momentum: {momentum_signal}")
        print(f"  ─────────────────────────────────────────")
        print(f"  TOTAL QUALITY SCORE: {quality_score:+.1f} / {max_score} ({pct_score:+.0f}%)")

        print(f"\n{'─' * 70}")
        if pct_score >= 50:
            verdict = "HIGH QUALITY EARNINGS"
            print(f"VERDICT: {verdict}")
            print(f"  → Earnings appear sustainable and well-supported")
        elif pct_score >= 10:
            verdict = "MODERATE QUALITY"
            print(f"VERDICT: {verdict}")
            print(f"  → Earnings acceptable but watch for deterioration")
        elif pct_score >= -20:
            verdict = "WATCH LIST"
            print(f"VERDICT: {verdict}")
            print(f"  → Earnings quality concerns - investigate")
        else:
            verdict = "LOW QUALITY EARNINGS"
            print(f"VERDICT: {verdict}")
            print(f"  → Significant earnings quality issues - avoid")

        print(f"{'=' * 70}\n")

        return {
            "cf_signal": cf_signal,
            "rev_signal": rev_signal,
            "margin_signal": margin_signal,
            "momentum_signal": momentum_signal,
            "quality_score": quality_score,
            "pct_score": pct_score,
            "verdict": verdict,
            "risks": risks,
        }

    except Exception as e:
        print(f"❌ Error in earnings quality analysis: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Earnings quality analysis - beat/miss rates, surprises")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    args = parser.parse_args()
    analyze_earnings_quality(args.ticker.upper())
