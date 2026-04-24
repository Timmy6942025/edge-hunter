#!/usr/bin/env python3
"""
Sector Rotation Script (Professional Quant)
================================================
- Sector momentum analysis
- Rotation signals
- Performance tracking
- Style classification
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

SECTORS = {
    'Technology': ['XLK', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META'],
    'Healthcare': ['XLV', 'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK'],
    'Finance': ['XLF', 'JPM', 'BAC', 'WFC', 'GS', 'MS'],
    'Energy': ['XLE', 'XOM', 'CVX', 'COP', 'SLB', 'EOG'],
    'Consumer': ['XLY', 'XLP', 'AMZN', 'WMT', 'HD', 'MCD'],
    'Industrials': ['XLI', 'CAT', 'BA', 'HON', 'UPS', 'GE'],
    'Materials': ['XLB', 'LIN', 'APD', 'SHW', 'FCX', 'NEM'],
    'Utilities': ['XLU', 'NEE', 'DUK', 'SO', 'D', 'AEP'],
    'Real Estate': ['XLRE', 'PLD', 'AMT', 'CCI', 'EQIX', 'SPG'],
    'Comm Services': ['XLC', 'T', 'VZ', 'TMUS', 'CHTR', 'EA'],
}

def analyze_sector(sector_name, tickers, period='3mo'):
    """Analyze a sector's performance using its ETF as proxy"""
    try:
        # Use only the sector ETF (first ticker) as proxy - faster than downloading all tickers
        etf_ticker = tickers[0]
        data = yf.download(etf_ticker, period=period, progress=False)
        if data.empty or len(data) < 20:
            return None
        
        data = flatten_yf_data(data)
        close = data['Close']
        
        returns = close.pct_change().dropna()
        avg_return = float(returns.mean()) * 252
        avg_vol = float(returns.std()) * np.sqrt(252)
        
        recent_perf = ((float(close.iloc[-1]) / float(close.iloc[-20])) - 1) * 100 if len(close) > 20 else 0
        
        return {
            'name': sector_name,
            'tickers': tickers,
            'annualized_return': avg_return * 100,
            'annualized_vol': avg_vol * 100,
            'sharpe': (avg_return / avg_vol) if avg_vol > 0 else 0,
            'recent_20d': float(recent_perf)
        }
    except Exception as e:
        return None

def main():
    parser = argparse.ArgumentParser(description='Sector Rotation Analysis')
    parser.add_argument('--period', default='3mo', help='Analysis period')
    parser.add_argument('--sector', help='Specific sector to analyze')
    args = parser.parse_args()
    
    print(f'\n{"="*70}')
    print(f'SECTOR ROTATION ANALYSIS')
    print(f'{"="*70}')
    print(f'Period: {args.period}')
    
    print(f'\n📥 Analyzing sectors...')
    
    results = []
    sectors_to_analyze = {args.sector: SECTORS[args.sector]} if args.sector and args.sector in SECTORS else SECTORS
    
    for sector_name, tickers in sectors_to_analyze.items():
        print(f'   Analyzing {sector_name}...', end=' ')
        result = analyze_sector(sector_name, tickers, args.period)
        if result:
            results.append(result)
            print('✅')
        else:
            print('❌')
    
    if not results:
        print('❌ No sectors analyzed')
        return
    
    results.sort(key=lambda x: x['annualized_return'], reverse=True)
    
    print(f'\n{"─"*70}')
    print(f'SECTOR PERFORMANCE RANKING')
    print(f'{"─"*70}')
    
    print(f'\n{"┌"+"─"*68+"┐"}')
    print(f'│{"Sector":<15} {"3M Ret":>10} {"20D Mom":>10} {"Vol":>10} {"Sharpe":>8} {"Rank":>6}│')
    print(f'├{"─"*68+"┤"}')
    
    for idx, r in enumerate(results, 1):
        mom_arrow = '▲' if r['recent_20d'] > 0 else '▼'
        print(f'│{r["name"]:<15} {r["annualized_return"]:>+9.1f}% {r["recent_20d"]:>+9.1f}%{mom_arrow} {r["annualized_vol"]:>9.1f}% {r["sharpe"]:>7.2f} {idx:>5} │')
    print(f'└{"─"*68+"┘"}')
    
    print(f'\n{"─"*70}')
    print(f'ROTATION SIGNALS')
    print(f'{"─"*70}')
    
    top_sectors = results[:3]
    bottom_sectors = results[-3:]
    
    print(f'\n🟢 LEADERS (Top 3):')
    for s in top_sectors:
        print(f'   {s["name"]}: {s["annualized_return"]:+.1f}%')
    
    print(f'\n🔴 LAGGARDS (Bottom 3):')
    for s in bottom_sectors:
        print(f'   {s["name"]}: {s["annualized_return"]:+.1f}%')
    
    # Momentum signals
    print(f'\n{"─"*70}')
    print(f'MOMENTUM ANALYSIS')
    print(f'{"─"*70}')
    
    # Compare short-term vs medium-term momentum
    for r in results:
        if r['recent_20d'] > 5 and r['annualized_return'] > 20:
            print(f'   📈 {r["name"]}: BREAKOUT MOMENTUM')
        elif r['recent_20d'] < -5 and r['annualized_return'] < -10:
            print(f'   📉 {r["name"]}: BREAKDOWN MOMENTUM')
        elif r['recent_20d'] > r['annualized_return']/4:
            print(f'   📊 {r["name"]}: ACCELERATING')
        elif r['recent_20d'] < -2 and r['annualized_return'] > 0:
            print(f'   ⚠️ {r["name"]}: DETERIORATING (watch for reversal)')
    
    print(f'\n{"─"*70}')
    print(f'PORTFOLIO RECOMMENDATIONS')
    print(f'{"─"*70}')
    
    if results:
        top = results[0]
        second = results[1]
        
        print(f'\n🏆 OVERWEIGHT: {top["name"]}')
        print(f'   Strong momentum: {top["annualized_return"]:+.1f}%')
        print(f'   Sharpe: {top["sharpe"]:.2f}')
        
        print(f'\n📊 MARKET WEIGHT: {second["name"]}')
        print(f'   Solid performance: {second["annualized_return"]:+.1f}%')
        
        worst = results[-1]
        print(f'\n🔻 UNDERWEIGHT: {worst["name"]}')
        print(f'   Weak momentum: {worst["annualized_return"]:+.1f}%')

if __name__ == '__main__':
    main()
