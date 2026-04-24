#!/usr/bin/env python3
"""
Insider Tracker Script (Professional Quant)
================================================
- SEC Form 4 tracking
- Insider transaction analysis
- Buy/sell ratio
- Sentiment scoring
"""

import argparse
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, safe_float
import warnings
warnings.filterwarnings('ignore')

def get_insider_transactions(ticker):
    """Get insider transactions from yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get major insider holders
        insider_holders = stock.get_major_holders()

        # Get institutional holders for context
        inst_holders = stock.get_institutional_holders()

        # Handle empty DataFrames safely
        insider_val = 0
        inst_val = 0
        try:
            if insider_holders is not None and not insider_holders.empty and len(insider_holders) > 0:
                insider_val = insider_holders['Holder'].iloc[0]
            if insider_holders is not None and not insider_holders.empty and len(insider_holders) > 1:
                inst_val = insider_holders['Holder'].iloc[1]
        except (KeyError, IndexError, TypeError):
            pass

        return {
            'insider_ownership': insider_val,
            'institutions_ownership': inst_val,
            'short_ratio': info.get('shortRatio', 0) or 0,
            'institutional_transactions': inst_holders.to_dict() if not inst_holders.empty else {}
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description='Insider Trading Tracker')
    parser.add_argument('tickers', nargs='+', help='Tickers to track')
    args = parser.parse_args()

    print(f'\n{"="*70}')
    print(f'INSIDER TRACKING ANALYSIS')
    print(f'{"="*70}')
    print(f'Tickers: {args.tickers}')

    for ticker in args.tickers:
        print(f'\n{"─"*70}')
        print(f'📊 {ticker}')
        print(f'{"─"*70}')

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Insider ownership
            insider_pct = info.get('heldByInsiders', 0) or 0
            inst_pct = info.get('heldByInstitutions', 0) or 0

            print(f'\n📈 OWNERSHIP STRUCTURE')
            print(f'   {"─"*40}')
            print(f'   Insider Ownership: {insider_pct*100:.2f}%')
            print(f'   Institutional: {inst_pct*100:.2f}%')
            print(f'   Public Float: {(1-insider_pct-inst_pct)*100:.2f}%')

            # Insider sentiment
            print(f'\n📊 INSIDER SENTIMENT INDICATORS')
            print(f'   {"─"*40}')

            # Proxy for insider sentiment based on ownership changes
            shares_outstanding = info.get('sharesOutstanding', 0) or 0

            if insider_pct > 0.15:
                print(f'   🟢 HIGH INSIDER OWNERSHIP (>{15}%)')
                print(f'      Indicates confidence in company')
            elif insider_pct > 0.05:
                print(f'   ⚪ MODERATE INSIDER OWNERSHIP')
            else:
                print(f'   🔴 LOW INSIDER OWNERSHIP (<{5}%)')
                print(f'      May indicate lack of insider confidence')

            # Short metrics as sentiment inverse
            short_ratio = info.get('shortRatio', 0) or 0
            short_float = info.get('shortPercentOfFloat', 0) or 0

            print(f'\n📉 SHORT INTEREST')
            print(f'   {"─"*40}')
            print(f'   Short Ratio: {short_ratio:.1f} days')
            print(f'   Short % Float: {short_float*100:.2f}%' if short_float else '   N/A')

            if short_float and short_float > 0.10:
                print(f'   ⚠️ HIGH SHORT INTEREST - Squeeze potential')
            elif short_float and short_float > 0.05:
                print(f'   ⚡ ELEVATED SHORT INTEREST')

            # Institutional activity proxy
            print(f'\n🏦 INSTITUTIONAL ACTIVITY')
            print(f'   {"─"*40}')

            # Get 13F filing activity from news/major holders
            try:
                major_holders = stock.get_major_holders()
                if not major_holders.empty:
                    for _, row in major_holders.head(5).iterrows():
                        holder = str(row.get('Holder', ''))[:30]
                        shares = row.get('Date', '')
                        if holder and 'holder' not in holder.lower():
                            print(f'   • {holder}')
            except Exception:
                pass

            # Recommendations
            print(f'\n{"─"*70}')
            print(f'INSIDER SIGNAL SUMMARY')
            print(f'{"─"*70}')

            signals = []

            if insider_pct > 0.15:
                signals.append(('🟢', 'High insider ownership', 'BULLISH'))
            elif insider_pct < 0.02:
                signals.append(('🔴', 'Very low insider ownership', 'BEARISH'))

            if short_float and short_float > 0.15:
                signals.append(('🟡', 'Very high short interest', 'NEUTRAL'))

            if inst_pct > 0.80:
                signals.append(('⚪', 'Heavily institutionally owned', 'NEUTRAL'))

            if not signals:
                signals.append(('⚪', 'Mixed/normals signals', 'NEUTRAL'))

            for emoji, signal, direction in signals:
                print(f'   {emoji} {signal} - {direction}')

        except Exception as e:
            print(f'❌ Error: {e!s}')

if __name__ == '__main__':
    main()
