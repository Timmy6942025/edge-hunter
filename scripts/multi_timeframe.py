#!/usr/bin/env python3
"""
Multi-Timeframe Analysis Script (Free, Pi-Friendly)
Analyzes: Daily/Weekly/Monthly alignment for trend confirmation
Uses yfinance for free data - no API keys needed
"""
import argparse
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def analyze_multitimeframe(ticker):
    """Multi-timeframe trend alignment analysis"""
    
    print(f"\n{'='*70}")
    print(f"MULTI-TIMEFRAME ANALYSIS: {ticker}")
    print(f"{'='*70}")
    
    try:
        monthly = yf.download(ticker, period="5y", interval="1mo", progress=False)
        weekly = yf.download(ticker, period="2y", interval="1wk", progress=False)
        daily = yf.download(ticker, period="1y", interval="1d", progress=False)
        
        if monthly.empty or weekly.empty or daily.empty:
            print("❌ Insufficient data for multi-timeframe analysis")
            return None
        
        for df in [monthly, weekly, daily]:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]
        
        def get_momentum(close, period=14):
            if len(close) < period + 1:
                return 50
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        
        def analyze_timeframe(df):
            close = df['Close']
            sma_20 = close.rolling(window=20).mean()
            sma_50 = close.rolling(window=50).mean()
            sma_200 = close.rolling(window=200).mean()
            
            current_price = float(close.iloc[-1])
            sma20_val = sma_20.iloc[-1] if not pd.isna(sma_20.iloc[-1]) else 0
            sma50_val = sma_50.iloc[-1] if not pd.isna(sma_50.iloc[-1]) else 0
            sma200_val = sma_200.iloc[-1] if not pd.isna(sma_200.iloc[-1]) else 0
            
            if sma20_val > 0 and sma50_val > 0:
                if sma20_val > sma50_val:
                    trend = "UPTREND" if sma50_val > sma200_val else "WEAK UPTREND"
                else:
                    trend = "DOWNTREND" if sma50_val < sma200_val else "WEAK DOWNTREND"
            else:
                trend = "NO TREND"
            
            price_vs_200ma = (current_price / sma200_val - 1) * 100 if sma200_val > 0 else 0
            rsi = get_momentum(close)
            
            return {
                "price": current_price,
                "sma20": sma20_val,
                "sma50": sma50_val,
                "sma200": sma200_val,
                "trend": trend,
                "rsi": rsi,
                "price_vs_200ma": price_vs_200ma
            }
        
        monthly_analysis = analyze_timeframe(monthly)
        weekly_analysis = analyze_timeframe(weekly)
        daily_analysis = analyze_timeframe(daily)
        
        def print_timeframe(name, data):
            print(f"\n{'─'*70}")
            print(f"{name} TIMEFRAME")
            print(f"{'─'*70}")
            print(f"  Price: ${data['price']:.2f}")
            print(f"  SMA(20): ${data['sma20']:.2f}")
            print(f"  SMA(50): ${data['sma50']:.2f}")
            print(f"  SMA(200): ${data['sma200']:.2f}")
            print(f"  Trend: {data['trend']}")
            print(f"  RSI(14): {data['rsi']:.1f}")
            print(f"  Price vs 200MA: {data['price_vs_200ma']:+.1f}%")
        
        print_timeframe("MONTHLY", monthly_analysis)
        print_timeframe("WEEKLY", weekly_analysis)
        print_timeframe("DAILY", daily_analysis)
        
        print(f"\n{'='*70}")
        print(f"TIMEFRAME ALIGNMENT ANALYSIS")
        print(f"{'='*70}")
        
        bullish_count = 0
        total_signals = 0
        
        if "UPTREND" in monthly_analysis['trend']:
            bullish_count += 2
            print(f"  Monthly: ✅ {monthly_analysis['trend']}")
        elif "DOWNTREND" in monthly_analysis['trend']:
            bullish_count -= 2
            print(f"  Monthly: ❌ {monthly_analysis['trend']}")
        else:
            print(f"  Monthly: ⚠️ {monthly_analysis['trend']}")
        total_signals += 2
        
        if "UPTREND" in weekly_analysis['trend']:
            bullish_count += 1.5
            print(f"  Weekly: ✅ {weekly_analysis['trend']}")
        elif "DOWNTREND" in weekly_analysis['trend']:
            bullish_count -= 1.5
            print(f"  Weekly: ❌ {weekly_analysis['trend']}")
        else:
            print(f"  Weekly: ⚠️ {weekly_analysis['trend']}")
        total_signals += 1.5
        
        if "UPTREND" in daily_analysis['trend']:
            bullish_count += 1
            print(f"  Daily: ✅ {daily_analysis['trend']}")
        elif "DOWNTREND" in daily_analysis['trend']:
            bullish_count -= 1
            print(f"  Daily: ❌ {daily_analysis['trend']}")
        else:
            print(f"  Daily: ⚠️ {daily_analysis['trend']}")
        total_signals += 1
        
        rsi_avg = (monthly_analysis['rsi'] + weekly_analysis['rsi'] + daily_analysis['rsi']) / 3
        if rsi_avg > 55:
            bullish_count += 0.5
            print(f"  RSI (avg): ✅ {rsi_avg:.1f} (bullish momentum)")
        elif rsi_avg < 45:
            bullish_count -= 0.5
            print(f"  RSI (avg): ❌ {rsi_avg:.1f} (bearish momentum)")
        else:
            print(f"  RSI (avg): ⚠️ {rsi_avg:.1f} (neutral)")
        total_signals += 0.5
        
        alignment_pct = (bullish_count / total_signals) * 100 if total_signals > 0 else 0
        
        print(f"\n{'─'*70}")
        print(f"ALIGNMENT SCORE: {alignment_pct:+.0f}%")
        
        if alignment_pct >= 60:
            verdict = "STRONG ALIGNMENT - TREND CONFIRMED"
        elif alignment_pct >= 20:
            verdict = "MODERATE ALIGNMENT - CAUTION ADVISED"
        elif alignment_pct >= -20:
            verdict = "MIXED SIGNALS - NO CLEAR TREND"
        elif alignment_pct >= -60:
            verdict = "COUNTER-TREND - OPPOSITE PREVAILS"
        else:
            verdict = "STRONG COUNTER-TREND - TREND REVERSAL LIKELY"
        
        print(f"  → {verdict}")
        
        print(f"\n{'─'*70}")
        print(f"TIMEFRAME CONFLICT CHECK")
        print(f"{'─'*70}")
        
        monthly_bull = "UPTREND" in monthly_analysis['trend']
        daily_bull = "UPTREND" in daily_analysis['trend']
        
        if monthly_bull and daily_bull:
            print("  ✅ ALL TIMEFRAMES BULLISH - High confidence signal")
            conflict_verdict = "NO CONFLICT"
        elif not monthly_bull and not daily_bull:
            print("  ❌ ALL TIMEFRAMES BEARISH - High confidence signal")
            conflict_verdict = "NO CONFLICT"
        elif monthly_bull and not daily_bull:
            print("  ⚠️ MONTHLY BULLISH / DAILY BEARISH - Daily pullback in uptrend")
            conflict_verdict = "CONFLICT - DAILY WINS SHORT TERM"
        elif not monthly_bull and daily_bull:
            print("  ⚠️ MONTHLY BEARISH / DAILY BULLISH - Potential reversal")
            conflict_verdict = "CONFLICT - MONTHLY WINS LONG TERM"
        else:
            print("  ⚠️ MIXED TIMEFRAMES")
            conflict_verdict = "CONFLICT - NO CLEAR DIRECTION"
        
        print(f"\n{'='*70}")
        print(f"FINAL VERDICT: {verdict}")
        print(f"{'='*70}")
        print(f"  Alignment Score: {alignment_pct:+.0f}%")
        print(f"  Conflict Status: {conflict_verdict}")
        print(f"  Recommendation: ", end="")
        
        if alignment_pct >= 60:
            print("TREND FOLLOWING - BUY on pullbacks")
        elif alignment_pct <= -60:
            print("TREND FOLLOWING - SELL on rallies")
        else:
            print("WAIT for better alignment")
        
        print(f"{'='*70}\n")
        
        return {
            "alignment_score": alignment_pct,
            "verdict": verdict,
            "conflict_verdict": conflict_verdict
        }
        
    except Exception as e:
        print(f"❌ Error in multi-timeframe analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-timeframe trend analysis")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    args = parser.parse_args()
    analyze_multitimeframe(args.ticker.upper())
