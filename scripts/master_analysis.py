#!/usr/bin/env python3
"""
Master Quantitative Analysis - Orchestrator
Runs ALL scripts and outputs structured data for AI synthesis.
NO fake recommendations - just raw data for the AI to analyze.
"""
import subprocess
import sys
import re
import argparse
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, extract_price_data, safe_float
from datetime import datetime

def run_master_analysis(ticker):
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n{'#'*80}")
    print(f"# MASTER QUANTITATIVE ANALYSIS: {ticker}")
    print(f"# CURRENT DATE: {today}")
    print(f"# DEEP THINKING PROTOCOL ACTIVATED")
    print(f"# NO FAKE RECOMMENDATIONS - DATA ONLY")
    print(f"{'#'*80}")
    
    results = {}
    
    # ==========================================================================
    # 1. Run forecast.py (Prophet + technical indicators)
    # ==========================================================================
    print(f"\n[1/8] Running forecast & technical indicators...")
    try:
        result = subprocess.run(
            [sys.executable, "forecast.py", ticker],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
        
        # Parse NEW output format from forecast.py
        # Extract prophet_change_pct
        change_match = re.search(r'prophet_change_pct: ([-+]?\d+\.\d+)', result.stdout)
        if change_match:
            results['prophet_change'] = float(change_match.group(1))
        
        # Extract RSI
        rsi_match = re.search(r'rsi: ([\d.]+)', result.stdout)
        if rsi_match:
            results['rsi'] = float(rsi_match.group(1))
        
        # Extract trend
        trend_match = re.search(r'trend: (\w+)', result.stdout)
        if trend_match:
            results['trend'] = trend_match.group(1)
        
        # Extract uncertainty
        uncertainty_match = re.search(r'uncertainty_range_pct: ([\d.]+)', result.stdout)
        if uncertainty_match:
            results['uncertainty'] = float(uncertainty_match.group(1))
        
        # Set forecast signal based on data (not fake recommendation)
        if results.get('prophet_change', 0) > 0 and results.get('rsi', 50) < 70:
            results['forecast_signal'] = 'BULLISH'
        elif results.get('prophet_change', 0) < 0 and results.get('rsi', 50) > 30:
            results['forecast_signal'] = 'BEARISH'
        else:
            results['forecast_signal'] = 'NEUTRAL'
        
    except Exception as e:
        print(f"Forecast error: {e}")
        results['forecast_signal'] = 'ERROR'
    
    # ==========================================================================
    # 2. Run backtest.py (STRICT quant rules applied)
    # ==========================================================================
    print(f"\n[2/8] Running backtest (NO look-ahead, with friction)...")
    try:
        result = subprocess.run(
            [sys.executable, "backtest.py", ticker],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
        
        # Parse backtest conviction
        if "CONVICTION: STRONG BUY" in result.stdout:
            results['backtest'] = 'STRONG BUY'
        elif "CONVICTION: BUY" in result.stdout:
            results['backtest'] = 'BUY'
        elif "CONVICTION: STRONG SELL" in result.stdout:
            results['backtest'] = 'STRONG SELL'
        else:
            results['backtest'] = 'SELL'
        
        # Parse alpha vs buy & hold
        alpha_match = re.search(r'Alpha Generated: ([+-]?\d+\.\d+)%', result.stdout)
        if alpha_match:
            results['alpha_vs_buy_hold'] = float(alpha_match.group(1))
        
        # Parse Sharpe
        sharpe_match = re.search(r'Sharpe: ([\d.]+)', result.stdout)
        if sharpe_match:
            results['backtest_sharpe'] = float(sharpe_match.group(1))
        
    except Exception as e:
        print(f"Backtest error: {e}")
        results['backtest'] = 'ERROR'
    
    # ==========================================================================
    # 3. Run risk_metrics.py
    # ==========================================================================
    print(f"\n[3/8] Calculating comprehensive risk metrics...")
    try:
        result = subprocess.run(
            [sys.executable, "risk_metrics.py", ticker],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
        
        if "RISK RATING:" in result.stdout:
            match = re.search(r'RISK RATING: (.+)', result.stdout)
            if match:
                results['risk'] = match.group(1)
        
        # Parse Sharpe
        sharpe_match = re.search(r'Sharpe Ratio: ([\d.]+)', result.stdout)
        if sharpe_match:
            results['sharpe'] = float(sharpe_match.group(1))
        
        # Parse max drawdown
        dd_match = re.search(r'Max Drawdown: ([\d.-]+)%', result.stdout)
        if dd_match:
            results['max_dd'] = float(dd_match.group(1))
        
    except Exception as e:
        print(f"Risk metrics error: {e}")
        results['risk'] = 'ERROR'
    
    # ==========================================================================
    # 4. Run sector_comparison.py
    # ==========================================================================
    print(f"\n[4/8] Running sector & peer comparison...")
    try:
        result = subprocess.run(
            [sys.executable, "sector_comparison.py", ticker, "--peers", "MSFT", "GOOGL", "META"],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
    except Exception as e:
        print(f"Sector comparison error: {e}")
    
    # ==========================================================================
    # 5. Run news_sentiment.py
    # ==========================================================================
    print(f"\n[5/8] Analyzing news sentiment...")
    try:
        result = subprocess.run(
            [sys.executable, "news_sentiment.py", ticker],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
    except Exception as e:
        print(f"News sentiment error: {e}")
    
    # ==========================================================================
    # 6. Kelly Criterion position sizing
    # ==========================================================================
    print(f"\n[6/8] Calculating Kelly Criterion position size...")
    try:
        result = subprocess.run(
            [sys.executable, "kelly_sizer.py", ticker],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
    except Exception as e:
        print(f"Kelly sizer error: {e}")
    
    # ==========================================================================
    # 7. Macro economic analysis
    # ==========================================================================
    print(f"\n[7/8] Analyzing macro environment...")
    try:
        result = subprocess.run(
            [sys.executable, "macro_analysis.py"],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
    except Exception as e:
        print(f"Macro analysis error: {e}")
    
    # ==========================================================================
    # 8. Get earnings context
    # ==========================================================================
    print(f"\n[8/8] Fetching earnings context...")
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        
        print(f"\nEARNINGS CONTEXT:")
        if 'trailingPE' in info and info['trailingPE']:
            print(f"  Trailing P/E: {info['trailingPE']:.2f}")
        if 'forwardPE' in info and info['forwardPE']:
            print(f"  Forward P/E: {info['forwardPE']:.2f}")
        if 'marketCap' in info and info['marketCap']:
            print(f"  Market Cap: ${info['marketCap']/1e9:.2f}B")
        if 'recommendationKey' in info:
            print(f"  Analyst Consensus: {info['recommendationKey']}")
    except Exception as e:
        print(f"  Earnings context error: {e}")
    
    # ==========================================================================
    # OUTPUT STRUCTURED DATA FOR AI SYNTHESIS
    # ==========================================================================
    print(f"\n{'='*80}")
    print(f"STRUCTURED DATA OUTPUT (for AI deep analysis)")
    print(f"{'='*80}")
    
    print(f"\nSIGNAL SUMMARY:")
    print(f"  Forecast Signal: {results.get('forecast_signal', 'N/A')}")
    print(f"    - Prophet Change: {results.get('prophet_change', 'N/A')}%")
    print(f"    - RSI: {results.get('rsi', 'N/A')}")
    print(f"    - Trend: {results.get('trend', 'N/A')}")
    print(f"    - Uncertainty: {results.get('uncertainty', 'N/A')}%")
    
    print(f"\n  Backtest Conviction: {results.get('backtest', 'N/A')}")
    print(f"    - Alpha vs Buy&Hold: {results.get('alpha_vs_buy_hold', 'N/A')}%")
    print(f"    - Sharpe: {results.get('backtest_sharpe', 'N/A')}")
    
    print(f"\n  Risk Rating: {results.get('risk', 'N/A')}")
    print(f"    - Sharpe: {results.get('sharpe', 'N/A')}")
    print(f"    - Max Drawdown: {results.get('max_dd', 'N/A')}%")
    
    print(f"\n{'='*80}")
    print(f"DEEP THINKING SYNTHESIS REQUIRED")
    print(f"{'='*80}")
    print(f"\n[INSTRUCTIONS TO AI]:")
    print(f"1. Read references/deep_analysis.md")
    print(f"2. Fill out references/deep_thought_template.md (500+ words)")
    print(f"3. Use the STRUCTURED DATA above")
    print(f"4. Do websearch for recent news/events")
    print(f"5. Synthesize decisive BUY/SELL/HOLD with confidence")
    print(f"6. NO disclaimers, NO weak language\n")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master quantitative analysis orchestrator")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    args = parser.parse_args()
    run_master_analysis(args.ticker)
