#!/usr/bin/env python3
"""
Correlation Matrix Script (Professional Quant)
================================================
- Pairwise correlation analysis
- Heatmap generation (ASCII)
- Rolling correlation tracking
- Diversification insights
"""

import argparse
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, safe_float
import warnings
warnings.filterwarnings('ignore')

def calculate_correlation_matrix(tickers, period='1y'):
    """Calculate correlation matrix for tickers"""
    # Download price data for all tickers
    raw = yf.download(tickers, period=period, progress=False)
    
    # Handle the price column - newer yfinance uses MultiIndex columns
    if isinstance(raw.columns, pd.MultiIndex):
        # MultiIndex: columns are (PriceType, Ticker)
        if 'Close' in raw.columns.get_level_values(0):
            data = raw['Close']
        elif 'Adj Close' in raw.columns.get_level_values(0):
            data = raw['Adj Close']
        else:
            data = raw.iloc[:, 0]
    else:
        # Flat columns - single ticker case
        if 'Close' in raw.columns:
            data = raw['Close']
        elif 'Adj Close' in raw.columns:
            data = raw['Adj Close']
        else:
            data = raw.iloc[:, 0]
    
    # Ensure data is a DataFrame
    if isinstance(data, pd.Series):
        data = data.to_frame()
    
    # Flatten if still MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(-1)
    
    # Calculate returns and correlation
    returns = data.pct_change().dropna()
    
    # Drop columns with any remaining NaN (illiquid tickers)
    if returns.isnull().any().any():
        returns = returns.dropna(axis=1, how='any')
    
    corr = returns.corr()
    
    return corr, returns

def main():
    parser = argparse.ArgumentParser(description='Correlation Matrix Analysis')
    parser.add_argument('tickers', nargs='+', help='Tickers to analyze')
    parser.add_argument('--period', default='1y', help='Data period')
    args = parser.parse_args()
    
    print(f'\n{"="*70}')
    print(f'CORRELATION MATRIX ANALYSIS')
    print(f'{"="*70}')
    print(f'Tickers: {args.tickers}')
    print(f'Period: {args.period}')
    
    if len(args.tickers) < 2:
        print('❌ Need at least 2 tickers')
        return
    
    print(f'\n📥 Downloading data...')
    corr, returns = calculate_correlation_matrix(args.tickers, args.period)
    
    print(f'\n{"─"*70}')
    print(f'CORRELATION MATRIX')
    print(f'{"─"*70}')
    
    # Print header
    print(f'\n    ', end='')
    for ticker in corr.columns:
        print(f'{ticker[:6]:>10}', end='')
    print()
    
    print(f'    {"─"*10*len(corr.columns)}')
    
    for row_ticker in corr.index:
        print(f'{row_ticker[:6]:>6}', end='')
        for col_ticker in corr.columns:
            val = float(corr.loc[row_ticker, col_ticker])
            if row_ticker == col_ticker:
                print(f'{"  1.00  ":>10}', end='')
            else:
                color = '🟢' if val > 0.5 else ('🔴' if val < -0.5 else '⚪')
                print(f'{color}{val:>7.2f} ', end='')
        print()
    
    print(f'\n{"─"*70}')
    print(f'KEY FINDINGS')
    print(f'{"─"*70}')
    
    # Find highest correlations
    corr_pairs = []
    for i in range(len(corr)):
        for j in range(i+1, len(corr)):
            corr_pairs.append((corr.index[i], corr.columns[j], float(corr.iloc[i, j])))
    
    corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    
    print(f'\n📊 Highest Correlations:')
    for pair in corr_pairs[:5]:
        direction = 'POSITIVE' if pair[2] > 0 else 'NEGATIVE'
        strength = 'STRONG' if abs(pair[2]) > 0.7 else ('MODERATE' if abs(pair[2]) > 0.4 else 'WEAK')
        print(f'   {pair[0]} / {pair[1]}: {pair[2]:+.2f} ({strength} {direction})')
    
    # Diversification analysis
    print(f'\n📈 DIVERSIFICATION ANALYSIS:')
    
    avg_corr = float(corr.values[np.triu_indices(len(corr), 1)].mean())
    print(f'   Average correlation: {avg_corr:.2f}')
    
    if avg_corr < 0.3:
        print(f'   ✅ GOOD DIVERSIFICATION - Low average correlation')
    elif avg_corr < 0.6:
        print(f'   ⚠️ MODERATE DIVERSIFICATION - Some correlation')
    else:
        print(f'   ❌ POOR DIVERSIFICATION - High correlation')
    
    # Find best diversification pairs
    low_corr = [p for p in corr_pairs if abs(p[2]) < 0.3]
    if low_corr:
        print(f'\n   Best for diversification:')
        for pair in low_corr[:3]:
            print(f'      {pair[0]} / {pair[1]}: {pair[2]:+.2f}')
    
    # Portfolio concentration risk
    print(f'\n{"─"*70}')
    print(f'RISK METRICS')
    print(f'{"─"*70}')
    
    # Correlation matrix determinant (diversification measure)
    try:
        det = float(np.linalg.det(corr.values))
        if det < 0.001:
            print(f'\n   ⚠️ HIGH CONCENTRATION RISK')
            print(f'      Near-singular correlation matrix')
            print(f'      Determinant: {det:.6f}')
        else:
            print(f'\n   ✅ Correlation matrix well-conditioned')
            print(f'      Determinant: {det:.6f}')
    except Exception:
        print(f'\n   Unable to calculate matrix properties')

if __name__ == '__main__':
    main()
