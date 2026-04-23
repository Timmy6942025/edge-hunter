#!/usr/bin/env python3
"""
Master Quantitative Analysis - The "Insane" Analysis
Combines ALL signals into one decisive investment thesis with deep reasoning
"""
import subprocess
import sys
import re
import yfinance as yf
import pandas as pd
import argparse

def get_earnings_context(ticker):
    """Get earnings info for context (free from yfinance)"""
    try:
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
        
        # Get earnings surprises if available
        try:
            earnings = stock.earnings
            if earnings is not None and len(earnings) > 0:
                last_earnings = earnings.iloc[-1]
                print(f"  Last Earnings: {last_earnings.get('Earnings', 'N/A')}")
        except:
            pass
            
    except Exception as e:
        print(f"  Earnings context error: {e}")

def run_master_analysis(ticker):
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n{'#'*80}")
    print(f"# MASTER QUANTITATIVE ANALYSIS: {ticker}")
    print(f"# CURRENT DATE: {today}")
    print(f"# DEEP THINKING PROTOCOL ACTIVATED")
    print(f"{'#'*80}")
        print(result.stdout)
        if "RECOMMENDATION: BUY" in result.stdout:
            results['forecast'] = 'BUY'
        elif "RECOMMENDATION: SELL" in result.stdout:
            results['forecast'] = 'SELL'
        else:
            results['forecast'] = 'HOLD'
        
        # Extract RSI for context
        rsi_match = re.search(r'RSI \(14\): ([\d.]+)', result.stdout)
        if rsi_match:
            results['rsi'] = float(rsi_match.group(1))
    except Exception as e:
        print(f"Forecast error: {e}")
        results['forecast'] = 'ERROR'
    
    # Run backtest
    print("\n[2/5] Running strategy backtests...")
    try:
        result = subprocess.run(
            [sys.executable, "backtest.py", ticker],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
        if "CONVICTION: STRONG BUY" in result.stdout:
            results['backtest'] = 'STRONG BUY'
        elif "CONVICTION: BUY" in result.stdout:
            results['backtest'] = 'BUY'
        elif "CONVICTION: STRONG SELL" in result.stdout:
            results['backtest'] = 'STRONG SELL'
        else:
            results['backtest'] = 'SELL'
    except Exception as e:
        print(f"Backtest error: {e}")
        results['backtest'] = 'ERROR'
    
    # Run risk metrics
    print("\n[3/5] Calculating comprehensive risk metrics...")
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
    except Exception as e:
        print(f"Risk metrics error: {e}")
        results['risk'] = 'ERROR'
    
    # Run sector comparison
    print("\n[4/6] Running sector & peer comparison...")
    try:
        result = subprocess.run(
            [sys.executable, "sector_comparison.py", ticker, "--peers", "MSFT", "GOOGL", "META"],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
    except Exception as e:
        print(f"Sector comparison error: {e}")
    
    # Run news sentiment
    print("\n[5/6] Analyzing news sentiment...")
    try:
        result = subprocess.run(
            [sys.executable, "news_sentiment.py", ticker],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
    except Exception as e:
        print(f"News sentiment error: {e}")
    
    # Try SEC filings (may fail due to SSL - SEC blocks automated requests)
    print("\n[6/7] Fetching SEC filings (skipped - SEC blocks requests)...")
    print("  TIP: Manually visit https://www.sec.gov for filings")
    # Disabled: SEC blocks automated requests with 403 Forbidden
    # try:
    #     result = subprocess.run(
    #         [sys.executable, "sec_filings.py", ticker],
    #         capture_output=True, text=True, cwd=".",
    #         timeout=10
    #     )
    #     print(result.stdout)
    # except Exception as e:
    #     print(f"SEC filings skipped: {e}")
    
    # Kelly Criterion position sizing
    print("\n[7/8] Calculating Kelly Criterion position size...")
    try:
        result = subprocess.run(
            [sys.executable, "kelly_sizer.py", ticker],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
    except Exception as e:
        print(f"Kelly sizer error: {e}")
    
    # Macro economic analysis
    print("\n[8/8] Analyzing macro environment...")
    try:
        result = subprocess.run(
            [sys.executable, "macro_analysis.py"],
            capture_output=True, text=True, cwd="."
        )
        print(result.stdout)
    except Exception as e:
        print(f"Macro analysis error: {e}")
    
    # Get earnings context
    print("\n[BONUS] Fetching earnings context...")
    get_earnings_context(ticker)
    
    # DEEP THINKING SECTION - This is where the AI must reason
    print(f"\n{'='*80}")
    print(f"DEEP THINKING SYNTHESIS - REQUIRES ANALYTICAL REASONING")
    print(f"{'='*80}")
    print(f"\n[INSTRUCTIONS TO AI: Produce 500+ words of deep analysis here,")
    print(f" covering ALL sections from references/deep_analysis.md]")
    print(f"\nSignal Conflicts:")
    print(f"  - Forecast says: {results.get('forecast', 'N/A')}")
    print(f"  - Backtest says: {results.get('backtest', 'N/A')}")
    print(f"  - Risk says: {results.get('risk', 'N/A')}")
    print(f"\nRSI Context: {results.get('rsi', 'N/A')}")
    if results.get('rsi'):
        if results['rsi'] > 70:
            print(f"  → Overbought! Potential reversal zone.")
        elif results['rsi'] < 30:
            print(f"  → Oversold! Potential bounce zone.")
    print(f"\n{'='*80}\n")
    
    # Final Verdict
    print(f"\n{'='*80}")
    print(f"FINAL QUANTITATIVE VERDICT: {ticker}")
    print(f"{'='*80}")
    
    # Count signals
    buy_signals = sum(1 for v in [results.get('forecast'), results.get('backtest')] 
                      if v in ['BUY', 'STRONG BUY'])
    sell_signals = sum(1 for v in [results.get('forecast'), results.get('backtest')] 
                       if v in ['SELL', 'STRONG SELL'])
    
    # Determine final verdict
    if results.get('backtest') == 'STRONG BUY' and results.get('forecast') == 'BUY':
        verdict = "STRONG BUY"
        confidence = "VERY HIGH"
    elif buy_signals >= 2:
        verdict = "BUY"
        confidence = "HIGH"
    elif sell_signals >= 2:
        verdict = "SELL"
        confidence = "HIGH"
    elif results.get('backtest') == 'STRONG SELL':
        verdict = "STRONG SELL"
        confidence = "VERY HIGH"
    else:
        verdict = "HOLD"
        confidence = "MEDIUM"
    
    print(f"\nSIGNAL SUMMARY:")
    print(f"  Forecast: {results.get('forecast', 'N/A')}")
    print(f"  Backtest: {results.get('backtest', 'N/A')}")
    print(f"  Risk: {results.get('risk', 'N/A')}")
    
    print(f"\n{'='*80}")
    print(f"  FINAL VERDICT: {verdict}")
    print(f"  CONFIDENCE: {confidence}")
    print(f"{'='*80}\n")
    
    print(f"\n[AI NEXT STEPS: Read references/deep_analysis.md and produce")
    print(f" deep 500+ word analysis with ALL required sections before")
    print(f" responding to user. Include specific numbers from above outputs.]\n")
    
    return verdict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master quantitative analysis")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    args = parser.parse_args()
    run_master_analysis(args.ticker)
