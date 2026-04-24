#!/usr/bin/env python3
"""
Fundamentals Screening Script (Free, Pi-Friendly)
Screens: P/E, P/B, debt/equity, revenue growth, margins
Uses yfinance for free data - no API keys needed
"""
import argparse
import numpy as np
import yfinance as yf
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, extract_price_data, safe_float
from datetime import datetime

def screen_fundamentals(ticker):
    """Comprehensive fundamental screening"""

    print(f"\n{'='*70}")
    print(f"FUNDAMENTAL SCREENING: {ticker}")
    print(f"{'='*70}")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # VALUATION METRICS
        print(f"\n{'─'*70}")
        print(f"VALUATION METRICS")
        print(f"{'─'*70}")

        pe_ratio = info.get('trailingPE') or info.get('forwardPE')
        peg_ratio = info.get('pegRatio')
        pb_ratio = info.get('priceToBook')
        ps_ratio = info.get('priceToSalesTrailing12Months')

        print(f"  Trailing P/E: {pe_ratio:.2f}" if pe_ratio else "  Trailing P/E: N/A")
        print(f"  Forward P/E: {info.get('forwardPE', 'N/A')}")
        print(f"  PEG Ratio: {peg_ratio:.2f}" if peg_ratio else "  PEG Ratio: N/A")
        print(f"  P/B Ratio: {pb_ratio:.2f}" if pb_ratio else "  P/B Ratio: N/A")
        print(f"  P/S Ratio: {ps_ratio:.2f}" if ps_ratio else "  P/S Ratio: N/A")

        val_score = 0
        if pe_ratio:
            if pe_ratio < 15:
                val_score += 2
                val_signal = "CHEAP"
            elif pe_ratio < 25:
                val_score += 1
                val_signal = "FAIR"
            elif pe_ratio < 40:
                val_score -= 1
                val_signal = "EXPENSIVE"
            else:
                val_score -= 2
                val_signal = "VERY EXPENSIVE"
        else:
            val_signal = "N/A"

        print(f"  → Valuation Signal: {val_signal}")

        # PROFITABILITY METRICS
        print(f"\n{'─'*70}")
        print(f"PROFITABILITY METRICS")
        print(f"{'─'*70}")

        profit_margin = info.get('profitMargins')
        operating_margin = info.get('operatingMargins')
        roe = info.get('returnOnEquity')
        roa = info.get('returnOnAssets')

        print(f"  Profit Margin: {profit_margin*100:.1f}%" if profit_margin else "  Profit Margin: N/A")
        print(f"  Operating Margin: {operating_margin*100:.1f}%" if operating_margin else "  Operating Margin: N/A")
        print(f"  ROE: {roe*100:.1f}%" if roe else "  ROE: N/A")
        print(f"  ROA: {roa*100:.1f}%" if roa else "  ROA: N/A")

        profit_score = 0
        if profit_margin:
            if profit_margin > 0.20:
                profit_score += 2
                profit_signal = "EXCELLENT"
            elif profit_margin > 0.10:
                profit_score += 1
                profit_signal = "GOOD"
            elif profit_margin > 0:
                profit_signal = "BREAKEVEN/LOW"
            else:
                profit_score -= 1
                profit_signal = "LOSING MONEY"
        else:
            profit_signal = "N/A"

        if roe:
            if roe > 0.20:
                profit_score += 1
            elif roe > 0.10:
                profit_score += 0.5
            elif roe < 0:
                profit_score -= 1

        print(f"  → Profitability Signal: {profit_signal}")

        # FINANCIAL HEALTH
        print(f"\n{'─'*70}")
        print(f"FINANCIAL HEALTH")
        print(f"{'─'*70}")

        debt_equity = info.get('debtToEquity')
        current_ratio = info.get('currentRatio')
        cash = info.get('totalCash')
        debt = info.get('totalDebt')
        fcf = info.get('freeCashflow')

        print(f"  Debt/Equity: {debt_equity:.1f}" if debt_equity else "  Debt/Equity: N/A")
        print(f"  Current Ratio: {current_ratio:.2f}" if current_ratio else "  Current Ratio: N/A")
        print(f"  Total Cash: ${cash/1e9:.2f}B" if cash else "  Total Cash: N/A")
        print(f"  Total Debt: ${debt/1e9:.2f}B" if debt else "  Total Debt: N/A")
        print(f"  Free Cash Flow: ${fcf/1e9:.2f}B" if fcf else "  Free Cash Flow: N/A")

        health_score = 0
        if debt_equity:
            if debt_equity < 0.5:
                health_score += 2
                health_signal = "EXCELLENT"
            elif debt_equity < 1.0:
                health_score += 1
                health_signal = "GOOD"
            elif debt_equity < 2.0:
                health_signal = "MODERATE"
            else:
                health_score -= 2
                health_signal = "HIGH LEVERAGE"
        else:
            health_signal = "N/A"

        if current_ratio:
            if current_ratio > 1.5:
                health_score += 1
            elif current_ratio < 1.0:
                health_score -= 1

        print(f"  → Financial Health Signal: {health_signal}")

        # GROWTH METRICS
        print(f"\n{'─'*70}")
        print(f"GROWTH METRICS")
        print(f"{'─'*70}")

        revenue_growth = info.get('revenueGrowth')
        earnings_growth = info.get('earningsGrowth')

        print(f"  Revenue Growth (YoY): {revenue_growth*100:.1f}%" if revenue_growth else "  Revenue Growth: N/A")
        print(f"  Earnings Growth (YoY): {earnings_growth*100:.1f}%" if earnings_growth else "  Earnings Growth: N/A")

        growth_score = 0
        if revenue_growth:
            if revenue_growth > 0.20:
                growth_score += 2
                growth_signal = "HIGH GROWTH"
            elif revenue_growth > 0.10:
                growth_score += 1
                growth_signal = "MODERATE GROWTH"
            elif revenue_growth > 0:
                growth_signal = "LOW GROWTH"
            else:
                growth_score -= 2
                growth_signal = "CONTRACTING"
        else:
            growth_signal = "N/A"

        print(f"  → Growth Signal: {growth_signal}")

        # DIVIDEND
        print(f"\n{'─'*70}")
        print(f"DIVIDEND & CAPITAL RETURN")
        print(f"{'─'*70}")

        dividend_yield = info.get('dividendYield')
        payout_ratio = info.get('payoutRatio')

        print(f"  Dividend Yield: {dividend_yield*100:.2f}%" if dividend_yield else "  Dividend Yield: N/A")
        print(f"  Payout Ratio: {payout_ratio*100:.1f}%" if payout_ratio else "  Payout Ratio: N/A")

        if dividend_yield:
            if dividend_yield > 0.03 and payout_ratio and payout_ratio < 0.6:
                div_signal = "SUSTAINABLE DIVIDEND"
            elif dividend_yield > 0.05:
                div_signal = "HIGH YIELD - VERIFY SUSTAINABILITY"
            else:
                div_signal = "LOW/NONE"
        else:
            div_signal = "NO DIVIDEND"

        print(f"  → Dividend Signal: {div_signal}")

        # ANALYST SENTIMENT
        print(f"\n{'─'*70}")
        print(f"ANALYST SENTIMENT")
        print(f"{'─'*70}")

        target_price = info.get('targetMeanPrice')
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        recom = info.get('recommendationKey')

        if target_price and current_price:
            upside = (target_price / current_price - 1) * 100
            print(f"  Target Price: ${target_price:.2f}")
            print(f"  Current Price: ${current_price:.2f}")
            print(f"  Upside/Downside: {upside:+.1f}%")

            if upside > 20:
                analyst_signal = "BULLISH"
            elif upside > 5:
                analyst_signal = "MODERATE BULLISH"
            elif upside > -5:
                analyst_signal = "NEUTRAL"
            else:
                analyst_signal = "BEARISH"
        else:
            analyst_signal = "N/A"

        print(f"  Recommendation: {recom.upper() if recom else 'N/A'}")
        print(f"  → Analyst Signal: {analyst_signal}")

        # OVERALL SCORE
        print(f"\n{'='*70}")
        print(f"FUNDAMENTAL SCORE SUMMARY")
        print(f"{'='*70}")

        total_score = val_score + profit_score + health_score + growth_score
        max_score = 8
        pct_score = (total_score / max_score) * 100

        print(f"\n  Component Scores:")
        print(f"    Valuation:     {val_signal:>15} ({val_score:+.1f})")
        print(f"    Profitability: {profit_signal:>15} ({profit_score:+.1f})")
        print(f"    Financial Hlth: {health_signal:>15} ({health_score:+.1f})")
        print(f"    Growth:        {growth_signal:>15} ({growth_score:+.1f})")
        print(f"  ─────────────────────────────────────────")
        print(f"    TOTAL SCORE: {total_score:+.1f} / {max_score} ({pct_score:+.0f}%)")

        print(f"\n{'─'*70}")
        if pct_score >= 60:
            verdict = "STRONG FUNDAMENTALS"
            print(f"VERDICT: {verdict} - Quality company, attractive valuation")
        elif pct_score >= 20:
            verdict = "MODERATE FUNDAMENTALS"
            print(f"VERDICT: {verdict} - Acceptable but watch for risks")
        elif pct_score >= -20:
            verdict = "WEAK FUNDAMENTALS"
            print(f"VERDICT: {verdict} - Significant concerns exist")
        else:
            verdict = "POOR FUNDAMENTALS"
            print(f"VERDICT: {verdict} - Avoid or deep value opportunity")

        print(f"{'='*70}\n")

        return {
            "valuation_signal": val_signal,
            "profitability_signal": profit_signal,
            "financial_health_signal": health_signal,
            "growth_signal": growth_signal,
            "total_score": total_score,
            "pct_score": pct_score,
            "verdict": verdict
        }

    except Exception as e:
        print(f"❌ Error screening fundamentals: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fundamental screening - P/E, margins, growth")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    args = parser.parse_args()
    screen_fundamentals(args.ticker.upper())
