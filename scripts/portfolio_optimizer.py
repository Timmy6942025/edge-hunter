#!/usr/bin/env python3
"""
Portfolio Optimizer Script (Professional Quant)
================================================
Implements:
- Mean-Variance Optimization (MVO)
- Efficient Frontier calculation
- Maximum Sharpe Ratio portfolio
- Risk Parity allocation
- Multiple optimization strategies

Uses PyPortfolioOpt for optimization + yfinance for data.
Install: pip install pypfopt matplotlib
"""

import argparse
import sys
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

def load_required_packages():
    '''Check and import optional packages'''
    try:
        from pypfopt import expected_returns, risk_models, EfficientFrontier, CLA
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        return True, expected_returns, risk_models, EfficientFrontier, CLA, plt
    except ImportError:
        return False, None, None, None, None, None

def calculate_manual_frontier(returns, n_portfolios=5000):
    """Calculate efficient frontier manually (no pypfopt needed)"""
    n_assets = returns.shape[1]
    
    # Calculate mean returns and covariance
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    # Generate random portfolios
    results = np.zeros((3, n_portfolios))
    weights_record = []
    
    for i in range(n_portfolios):
        weights = np.random.random(n_assets)
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        results[0, i] = portfolio_return
        results[1, i] = portfolio_std
        results[2, i] = (portfolio_return - 0.02) / portfolio_std if portfolio_std > 0 else 0  # Sharpe (2% risk-free)
    
    # Find max Sharpe
    max_sharpe_idx = np.argmax(results[2])
    max_sharpe_weights = weights_record[max_sharpe_idx]
    
    # Find min volatility
    min_vol_idx = np.argmin(results[1])
    min_vol_weights = weights_record[min_vol_idx]
    
    return {
        'results': results,
        'max_sharpe_weights': max_sharpe_weights,
        'max_sharpe_return': results[0, max_sharpe_idx],
        'max_sharpe_vol': results[1, max_sharpe_idx],
        'max_sharpe_ratio': results[2, max_sharpe_idx],
        'min_vol_weights': min_vol_weights,
        'min_vol_return': results[0, min_vol_idx],
        'min_vol_vol': results[1, min_vol_idx],
        'mean_returns': mean_returns,
        'cov_matrix': cov_matrix
    }

def calculate_risk_parity(returns):
    """Simple risk parity allocation"""
    cov_matrix = returns.cov() * 252
    
    # Inverse volatility weighting
    vols = np.sqrt(np.diag(cov_matrix))
    inv_vols = 1.0 / vols
    weights = inv_vols / np.sum(inv_vols)
    
    return weights

def main():
    parser = argparse.ArgumentParser(description='Portfolio Optimization')
    parser.add_argument('tickers', nargs='+', help='Tickers for portfolio')
    parser.add_argument('--period', default='2y', help='Data period')
    parser.add_argument('--portfolios', type=int, default=5000, help='Random portfolios')
    args = parser.parse_args()
    
    print(f'\n{"="*70}')
    print(f'PORTFOLIO OPTIMIZATION')
    print(f'{"="*70}')
    print(f'Tickers: {args.tickers}')
    print(f'Period: {args.period}')
    
    if len(args.tickers) < 2:
        print('❌ Need at least 2 tickers for portfolio optimization')
        return
    
    # Download data
    print(f'\n📥 Downloading price data...')
    raw = yf.download(args.tickers, period=args.period, progress=False)
    
    # Handle MultiIndex columns from yfinance
    if isinstance(raw.columns, pd.MultiIndex):
        # columns are (PriceType, Ticker) - extract Close prices
        if 'Close' in raw.columns.get_level_values(0):
            data = raw['Close']
        elif 'Adj Close' in raw.columns.get_level_values(0):
            data = raw['Adj Close']
        else:
            print('❌ Could not find price data')
            return
    else:
        if 'Close' in raw.columns:
            data = raw['Close']
        else:
            print('❌ Could not find price data')
            return
    
    if isinstance(data, pd.Series):
        data = data.to_frame()
    
    # Flatten any remaining MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(-1)
    
    if data.empty:
        print('❌ No price data available')
        return
    
    # Calculate returns
    returns = data.pct_change().dropna()
    
    if returns.empty or len(returns) < 30:
        print('❌ Insufficient data for optimization')
        return
    
    print(f'   Data points: {len(returns)}')
    print(f'   Tickers: {list(returns.columns)}')
    
    # ========== MANUAL EFFICIENT FRONTIER ==========
    print(f'\n{"─"*70}')
    print(f'EFFICIENT FRONTIER (Monte Carlo)')
    print(f'{"─"*70}')
    print(f'   Generating {args.portfolios} random portfolios...')
    
    frontier = calculate_manual_frontier(returns, args.portfolios)
    
    # Results
    print(f'\n📊 MAX SHARPE RATIO PORTFOLIO:')
    print(f'   Expected Return: {frontier["max_sharpe_return"]*100:.2f}%')
    print(f'   Volatility: {frontier["max_sharpe_vol"]*100:.2f}%')
    print(f'   Sharpe Ratio: {frontier["max_sharpe_ratio"]:.3f}')
    print(f'\n   Weights:')
    for i, ticker in enumerate(returns.columns):
        w = frontier['max_sharpe_weights'][i]
        if w > 0.01:
            print(f'      {ticker}: {w*100:.1f}%')
    
    print(f'\n📊 MINIMUM VOLATILITY PORTFOLIO:')
    print(f'   Expected Return: {frontier["min_vol_return"]*100:.2f}%')
    print(f'   Volatility: {frontier["min_vol_vol"]*100:.2f}%')
    print(f'\n   Weights:')
    for i, ticker in enumerate(returns.columns):
        w = frontier['min_vol_weights'][i]
        if w > 0.01:
            print(f'      {ticker}: {w*100:.1f}%')
    
    # ========== RISK PARITY ==========
    rp_weights = calculate_risk_parity(returns)
    
    rp_return = np.dot(rp_weights, frontier['mean_returns'])
    rp_vol = np.sqrt(np.dot(rp_weights.T, np.dot(frontier['cov_matrix'], rp_weights)))
    rp_sharpe = (rp_return - 0.02) / rp_vol if rp_vol > 0 else 0
    
    print(f'\n{"─"*70}')
    print(f'RISK PARITY PORTFOLIO (Equal Risk Contribution)')
    print(f'{"─"*70}')
    print(f'   Expected Return: {rp_return*100:.2f}%')
    print(f'   Volatility: {rp_vol*100:.2f}%')
    print(f'   Sharpe Ratio: {rp_sharpe:.3f}')
    print(f'\n   Weights:')
    for i, ticker in enumerate(returns.columns):
        w = rp_weights[i]
        print(f'      {ticker}: {w*100:.1f}%')
    
    # ========== EQUAL WEIGHT BENCHMARK ==========
    eq_weights = np.ones(len(returns.columns)) / len(returns.columns)
    eq_return = np.dot(eq_weights, frontier['mean_returns'])
    eq_vol = np.sqrt(np.dot(eq_weights.T, np.dot(frontier['cov_matrix'], eq_weights)))
    eq_sharpe = (eq_return - 0.02) / eq_vol if eq_vol > 0 else 0
    
    print(f'\n{"─"*70}')
    print(f'EQUAL WEIGHT BENCHMARK')
    print(f'{"─"*70}')
    print(f'   Expected Return: {eq_return*100:.2f}%')
    print(f'   Volatility: {eq_vol*100:.2f}%')
    print(f'   Sharpe Ratio: {eq_sharpe:.3f}')
    
    # ========== COMPARISON TABLE ==========
    print(f'\n{"─"*70}')
    print(f'STRATEGY COMPARISON')
    print(f'{"─"*70}')
    print(f'\n{"┌"+"─"*68+"┐"}')
    print(f'│{"Strategy":<20} {"Return":>10} {"Volatility":>12} {"Sharpe":>10} {"Rating":>8}│')
    print(f'├{"─"*68+"┤"}')
    
    strategies = [
        ('Max Sharpe', frontier['max_sharpe_return'], frontier['max_sharpe_vol'], frontier['max_sharpe_ratio']),
        ('Min Volatility', frontier['min_vol_return'], frontier['min_vol_vol'], (frontier['min_vol_return']-0.02)/frontier['min_vol_vol'] if frontier['min_vol_vol'] > 0 else 0),
        ('Risk Parity', rp_return, rp_vol, rp_sharpe),
        ('Equal Weight', eq_return, eq_vol, eq_sharpe),
    ]
    
    for name, ret, vol, sharpe in strategies:
        rating = '⭐⭐⭐' if sharpe > 1.0 else ('⭐⭐' if sharpe > 0.5 else '⭐')
        print(f'│{name:<20} {ret*100:>+9.2f}% {vol*100:>11.2f}% {sharpe:>9.3f} {rating:>8}│')
    print(f'└{"─"*68+"┘"}')
    
    # ========== RECOMMENDATION ==========
    print(f'\n{"─"*70}')
    print(f'OPTIMAL ALLOCATION RECOMMENDATION')
    print(f'{"─"*70}')
    
    # Best strategy based on Sharpe
    best_idx = np.argmax([s[3] for s in strategies])
    best = strategies[best_idx]
    
    if best_idx == 0:
        print(f'\n   🏆 RECOMMENDED: Max Sharpe Ratio Portfolio')
        for i, ticker in enumerate(returns.columns):
            w = frontier['max_sharpe_weights'][i]
            if w > 0.01:
                print(f'      {ticker}: {w*100:.1f}%')
    elif best_idx == 2:
        print(f'\n   🏆 RECOMMENDED: Risk Parity Portfolio')
        for i, ticker in enumerate(returns.columns):
            w = rp_weights[i]
            print(f'      {ticker}: {w*100:.1f}%')
    else:
        print(f'\n   🏆 RECOMMENDED: {best[0]} Portfolio')
    
    print(f'   Expected Return: {best[1]*100:.2f}%')
    print(f'   Sharpe Ratio: {best[3]:.3f}')
    
    # ========== PyPortfolioOpt (if available) ==========
    has_pypfopt, er_pkg, rm_pkg, ef_pkg, cla_pkg, plt_pkg = load_required_packages()
    
    if has_pypfopt:
        print(f'\n{"─"*70}')
        print(f'PyPortfolioOpt ANALYSIS (Advanced)')
        print(f'{"─"*70}')
        
        try:
            mu = er_pkg.mean_historical_return(data)
            S = rm_pkg.sample_cov(data)
            
            ef = ef_pkg(mu, S)
            ef.max_sharpe()
            pypfopt_weights = ef.clean_weights()
            
            print(f'\n   PyPortfolioOpt Max Sharpe Weights:')
            for ticker, weight in pypfopt_weights.items():
                if weight > 0.01:
                    print(f'      {ticker}: {weight*100:.1f}%')
            
            performance = ef.portfolio_performance()
            print(f'\n   Expected Return: {performance[0]*100:.2f}%')
            print(f'   Volatility: {performance[1]*100:.2f}%')
            print(f'   Sharpe: {performance[2]:.3f}')
        except Exception as e:
            print(f'   ⚠️ PyPortfolioOpt error: {e}')
    else:
        print(f'\n💡 Install PyPortfolioOpt for advanced optimization: pip install pypfopt')

if __name__ == '__main__':
    main()
