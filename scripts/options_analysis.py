#!/usr/bin/env python3
"""
Options Analysis Script (Free, Pi-Friendly)
Analyzes: IV, put/call ratio, gamma exposure, options flow
Uses yfinance for free options data - no API keys needed
"""
import argparse
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def analyze_options(ticker):
    """Comprehensive options analysis using free yfinance data"""

    print(f"\n{'='*70}")
    print(f"OPTIONS ANALYSIS: {ticker}")
    print(f"{'='*70}")

    try:
        stock = yf.Ticker(ticker)

        # Get stock info for current price
        info = stock.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('navPrice')
        if not current_price:
            hist = stock.history(period="1d")
            current_price = float(hist['Close'].iloc[-1]) if not hist.empty else None

        if not current_price:
            print("Could not get current price. Trying historical data...")
            hist = stock.history(period="5d")
            current_price = float(hist['Close'].iloc[-1]) if not hist.empty else None

        if not current_price:
            print("❌ Could not determine current price. Options analysis unavailable.")
            return None

        print(f"Current Price: ${current_price:.2f}")

        # Get available expiration dates
        expirations = stock.options
        if not expirations:
            print("❌ No options data available for this ticker")
            return None

        print(f"Available expirations: {len(expirations)} dates")

        # Aggregate all options data
        all_calls = []
        all_puts = []

        for exp in expirations[:6]:  # Analyze up to 6 nearest expirations
            try:
                opt = stock.option_chain(exp)
                calls = opt.calls.copy()
                puts = opt.puts.copy()
                calls['expiration'] = exp
                puts['expiration'] = exp
                all_calls.append(calls)
                all_puts.append(puts)
            except Exception:
                continue

        if not all_calls:
            print("❌ Could not fetch options chain data")
            return None

        calls_df = pd.concat(all_calls, ignore_index=True)
        puts_df = pd.concat(all_puts, ignore_index=True)

        # ========== PUT/CALL RATIO ANALYSIS ==========
        total_put_vol = puts_df['volume'].sum()
        total_call_vol = calls_df['volume'].sum()
        total_put_oi = puts_df['openInterest'].sum()
        total_call_oi = calls_df['openInterest'].sum()

        put_call_vol = total_put_vol / total_call_vol if total_call_vol > 0 else 0
        put_call_oi = total_put_oi / total_call_oi if total_call_oi > 0 else 0

        print(f"\n{'─'*70}")
        print(f"PUT/CALL RATIO ANALYSIS")
        print(f"{'─'*70}")
        print(f"  Put/Call Volume Ratio: {put_call_vol:.2f}")
        print(f"  Put/Call OI Ratio: {put_call_oi:.2f}")

        # Interpretation
        if put_call_vol > 1.2:
            print(f"  → BEARISH signal: High put buying (hedging/bearish)")
            pc_signal = "BEARISH"
        elif put_call_vol < 0.7:
            print(f"  → BULLISH signal: High call buying (speculative bullish)")
            pc_signal = "BULLISH"
        else:
            print(f"  → NEUTRAL: Balanced put/call activity")
            pc_signal = "NEUTRAL"

        # ========== IMPLIED VOLATILITY ANALYSIS ==========
        print(f"\n{'─'*70}")
        print(f"IMPLIED VOLATILITY (IV) ANALYSIS")
        print(f"{'─'*70}")

        # Near-term ATM options
        near_calls = calls_df[calls_df['expiration'] == expirations[0]].copy()
        near_puts = puts_df[puts_df['expiration'] == expirations[0]].copy()

        if not near_calls.empty and 'impliedVolatility' in near_calls.columns:
            near_calls['dist_from_atm'] = abs(near_calls['strike'] - current_price)
            near_puts['dist_from_atm'] = abs(near_puts['strike'] - current_price)

            atm_calls_iv = near_calls.nsmallest(5, 'dist_from_atm')['impliedVolatility'].mean()
            atm_puts_iv = near_puts.nsmallest(5, 'dist_from_atm')['impliedVolatility'].mean()

            avg_iv = (atm_calls_iv + atm_puts_iv) / 2

            print(f"  ATM Implied Volatility (near-term): {avg_iv*100:.1f}%")
            print(f"  IV Interpretation:")
            if avg_iv > 0.5:
                print(f"    → HIGH IV: Options are EXPENSIVE (high uncertainty)")
                iv_signal = "HIGH"
            elif avg_iv > 0.3:
                print(f"    → MODERATE IV: Normal market conditions")
                iv_signal = "MODERATE"
            else:
                print(f"    → LOW IV: Options are CHEAP (stable/undervalued)")
                iv_signal = "LOW"

            print(f"  → IV Signal: {iv_signal}")
        else:
            avg_iv = 0
            iv_signal = "UNKNOWN"
            print("  IV data not available from yfinance")

        # ========== GAMMA EXPOSURE (GEX) ==========
        print(f"\n{'─'*70}")
        print(f"GAMMA EXPOSURE (GEX) ANALYSIS")
        print(f"{'─'*70}")

        if not near_calls.empty and 'impliedVolatility' in near_calls.columns:
            gamma_calls = near_calls['openInterest'] * near_calls['strike'] * near_calls['impliedVolatility'] * 0.01
            gamma_puts = near_puts['openInterest'] * near_puts['strike'] * near_puts['impliedVolatility'] * 0.01

            total_call_gamma = gamma_calls.sum()
            total_put_gamma = gamma_puts.sum()
            net_gamma = total_call_gamma - total_put_gamma

            print(f"  Call Gamma Exposure: ${total_call_gamma/1e6:.2f}M")
            print(f"  Put Gamma Exposure: ${total_put_gamma/1e6:.2f}M")
            print(f"  Net Gamma: ${net_gamma/1e6:.2f}M")

            if net_gamma > 0:
                print(f"  → POSITIVE GEX: Market makers buying dips (support)")
                gex_signal = "SUPPORT"
            else:
                print(f"  → NEGATIVE GEX: Market makers selling rallies (resistance)")
                gex_signal = "RESISTANCE"

            near_calls['gamma'] = near_calls['openInterest'] * near_calls['impliedVolatility']
            near_puts['gamma'] = near_puts['openInterest'] * near_puts['impliedVolatility']

            if 'gamma' in near_calls.columns and not near_calls['gamma'].isna().all():
                max_call_gamma_strike = near_calls.loc[near_calls['gamma'].idxmax(), 'strike']
                max_put_gamma_strike = near_puts.loc[near_puts['gamma'].idxmax(), 'strike']
            else:
                max_call_gamma_strike = current_price
                max_put_gamma_strike = current_price

            print(f"  Max Call Gamma Strike: ${max_call_gamma_strike:.2f}")
            print(f"  Max Put Gamma Strike: ${max_put_gamma_strike:.2f}")
        else:
            gex_signal = "UNKNOWN"
            max_call_gamma_strike = current_price
            max_put_gamma_strike = current_price
            print("  Gamma data not available")

        # ========== UNUSUAL OPTIONS ACTIVITY ==========
        print(f"\n{'─'*70}")
        print(f"OPTIONS FLOW SUMMARY")
        print(f"{'─'*70}")

        if not calls_df.empty:
            vol_threshold = calls_df['volume'].quantile(0.9)
            high_vol_calls = calls_df[calls_df['volume'] >= vol_threshold]
            if not high_vol_calls.empty:
                print(f"  High Volume Calls (>90th percentile):")
                for _, row in high_vol_calls.head(3).iterrows():
                    iv = row['impliedVolatility'] * 100
                    print(
                        f"    Strike ${row['strike']:.0f} | "
                        f"Vol: {row['volume']:,.0f} | "
                        f"IV: {iv:.1f}% | "
                        f"OI: {row['openInterest']:,.0f}"
                    )

        if not puts_df.empty:
            vol_threshold = puts_df['volume'].quantile(0.9)
            high_vol_puts = puts_df[puts_df['volume'] >= vol_threshold]
            if not high_vol_puts.empty:
                print(f"\n  High Volume Puts (>90th percentile):")
                for _, row in high_vol_puts.head(3).iterrows():
                    iv = row['impliedVolatility'] * 100
                    print(
                        f"    Strike ${row['strike']:.0f} | "
                        f"Vol: {row['volume']:,.0f} | "
                        f"IV: {iv:.1f}% | "
                        f"OI: {row['openInterest']:,.0f}"
                    )

        # ========== SYNTHESIS ==========
        print(f"\n{'='*70}")
        print(f"OPTIONS VERDICT")
        print(f"{'='*70}")

        signals = [pc_signal, iv_signal, gex_signal]
        bullish = signals.count("BULLISH") + signals.count("SUPPORT") + signals.count("LOW")
        bearish = signals.count("BEARISH") + signals.count("RESISTANCE") + signals.count("HIGH")

        if bullish > bearish:
            verdict = "OPTIONS BULLISH"
        elif bearish > bullish:
            verdict = "OPTIONS BEARISH"
        else:
            verdict = "OPTIONS NEUTRAL"

        print(f"  Overall: {verdict} ({bullish} bullish vs {bearish} bearish signals)")
        print(f"\n  Put/Call Ratio: {pc_signal}")
        print(f"  IV Level: {iv_signal}")
        print(f"  Gamma Exposure: {gex_signal}")
        print(f"  Key Levels: Support ${max_put_gamma_strike:.0f} | Resistance ${max_call_gamma_strike:.0f}")
        print(f"{'='*70}\n")

        return {
            "put_call_vol": put_call_vol,
            "avg_iv": avg_iv * 100,
            "iv_signal": iv_signal,
            "net_gamma": net_gamma,
            "gex_signal": gex_signal,
            "support_level": max_put_gamma_strike,
            "resistance_level": max_call_gamma_strike,
            "verdict": verdict
        }

    except KeyError as e:
        print(f"❌ Error analyzing options: Missing data - {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Options analysis - IV, put/call ratio, gamma exposure")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    args = parser.parse_args()
    analyze_options(args.ticker.upper())
