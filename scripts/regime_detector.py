#!/usr/bin/env python3
"""
Market Regime Detector Script (Professional Quant)
================================================
- Bull/bear/sideways detection
- Volatility regime analysis
- Trend strength measurement
- Regime change signals
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

def detect_regime(data, short_window=20, long_window=50):
    """Detect market regime from price data"""
    
    # Calculate returns
    returns = data['Close'].pct_change().dropna()
    
    # Calculate moving averages
    ma_short = data['Close'].rolling(short_window).mean()
    ma_long = data['Close'].rolling(long_window).mean()
    
    # Calculate volatility
    volatility_20d = returns.tail(20).std() * np.sqrt(252)
    volatility_50d = returns.tail(50).std() * np.sqrt(252) if len(returns) >= 50 else volatility_20d
    
    # Trend strength
    trend_50d = float(((data['Close'].iloc[-1] / data['Close'].iloc[-50]) - 1) * 100) if len(data) > 50 else 0
    
    # MA slope
    ma_slope = float((ma_short.iloc[-1] - ma_short.iloc[-5]) / ma_short.iloc[-5] * 100) if len(ma_short) > 5 and ma_short.iloc[-5] != 0 else 0
    
    # Determine regime - force scalar comparisons
    ma_short_val = float(ma_short.iloc[-1])
    ma_long_val = float(ma_long.iloc[-1])
    
    if ma_short_val > ma_long_val and trend_50d > 0 and ma_slope > 0:
        regime = 'BULL'
        confidence = min(100, int(trend_50d * 5 + abs(ma_slope) * 10))
    elif ma_short_val < ma_long_val and trend_50d < 0 and ma_slope < 0:
        regime = 'BEAR'
        confidence = min(100, int(abs(trend_50d) * 5 + abs(ma_slope) * 10))
    else:
        regime = 'SIDEWAYS'
        confidence = 50
    
    return {
        'regime': regime,
        'confidence': confidence,
        'volatility_20d': float(volatility_20d),
        'volatility_50d': float(volatility_50d),
        'trend_50d': trend_50d,
        'ma_slope': ma_slope,
        'ma_short': ma_short_val,
        'ma_long': ma_long_val
    }

def detect_regime_change(data, short_window=20, long_window=50):
    """Detect recent regime changes"""
    changes = []
    
    for i in range(max(long_window, len(data) - 60), len(data)):
        if i < long_window:
            continue
        window = data.iloc[:i]
        regime = detect_regime(window, short_window, long_window)
        changes.append(regime['regime'])
    
    # Check for regime changes
    if len(changes) >= 2:
        if changes[-1] != changes[-2]:
            return {'change': True, 'from': changes[-2], 'to': changes[-1]}
    return {'change': False, 'current': changes[-1] if changes else 'UNKNOWN'}

def main():
    parser = argparse.ArgumentParser(description='Market Regime Detection')
    parser.add_argument('ticker', help='Ticker or index to analyze (e.g. SPY, QQQ)')
    parser.add_argument('--period', default='1y', help='Data period')
    args = parser.parse_args()
    
    print(f'\n{"="*70}')
    print(f'MARKET REGIME DETECTION')
    print(f'{"="*70}')
    print(f'Ticker: {args.ticker}')
    print(f'Period: {args.period}')
    
    data = yf.download(args.ticker, period=args.period, progress=False)
    if data.empty:
        print('❌ No data available')
        return
    
    data = flatten_yf_data(data)
    
    # Detect current regime
    regime = detect_regime(data)
    
    print(f'\n{"─"*70}')
    print(f'CURRENT REGIME')
    print(f'{"─"*70}')
    
    if regime['regime'] == 'BULL':
        print(f'   🟢 BULL MARKET')
    elif regime['regime'] == 'BEAR':
        print(f'   🔴 BEAR MARKET')
    else:
        print(f'   🟡 SIDEWAYS/TRANSITIONAL')
    
    print(f'   Confidence: {regime["confidence"]}%')
    
    print(f'\n{"─"*70}')
    print(f'REGIME METRICS')
    print(f'{"─"*70}')
    
    print(f'   Trend (50d): {regime["trend_50d"]:+.1f}%')
    print(f'   MA Slope: {regime["ma_slope"]:+.2f}%')
    print(f'   MA Short (20d): ${regime["ma_short"]:.2f}')
    print(f'   MA Long (50d): ${regime["ma_long"]:.2f}')
    
    print(f'\n{"─"*70}')
    print(f'VOLATILITY REGIME')
    print(f'{"─"*70}')
    
    vol_20 = regime['volatility_20d']
    vol_50 = regime['volatility_50d']
    
    print(f'   20d Volatility: {vol_20:.1f}%')
    print(f'   50d Volatility: {vol_50:.1f}%')
    
    if vol_20 > 40:
        print(f'   ⚠️ HIGH VOLATILITY - Risk-off regime')
    elif vol_20 > 25:
        print(f'   📊 ELEVATED VOLATILITY - Cautious')
    elif vol_20 > 15:
        print(f'   ✅ NORMAL VOLATILITY')
    else:
        print(f'   🟢 LOW VOLATILITY - Risk-on regime')
    
    # Volatility trend
    if vol_20 > vol_50 * 1.2:
        print(f'   📈 Volatility RISING - increasing uncertainty')
    elif vol_20 < vol_50 * 0.8:
        print(f'   📉 Volatility FALLING - calming market')
    else:
        print(f'   ➡️ Volatility STABLE')
    
    # Detect regime change
    change = detect_regime_change(data)
    
    print(f'\n{"─"*70}')
    print(f'REGIME CHANGE DETECTION')
    print(f'{"─"*70}')
    
    if change['change']:
        print(f'   ⚠️ REGIME CHANGE DETECTED!')
        print(f'   {change["from"]} → {change["to"]}')
        print(f'   This signals a potential shift in market dynamics')
    else:
        print(f'   ✅ No regime change detected')
        print(f'   Current: {change["current"]}')
    
    # Trading implications
    print(f'\n{"─"*70}')
    print(f'TRADING IMPLICATIONS')
    print(f'{"─"*70}')
    
    current_price = float(data['Close'].iloc[-1])
    
    if regime['regime'] == 'BULL':
        print(f'   Strategy: FAVOR LONG POSITIONS')
        print(f'   Sizing: Can increase position size (trend support)')
        print(f'   Stops: Use trailing stops to ride the trend')
    elif regime['regime'] == 'BEAR':
        print(f'   Strategy: FAVOR SHORT OR CASH')
        print(f'   Sizing: Reduce position size (counter-trend risk)')
        print(f'   Stops: Use tight stops - rallies may fail')
    else:
        print(f'   Strategy: NEUTRAL / RANGE-BOUND')
        print(f'   Sizing: Standard position size')
        print(f'   Approach: Mean reversion strategies may work')

if __name__ == '__main__':
    main()
