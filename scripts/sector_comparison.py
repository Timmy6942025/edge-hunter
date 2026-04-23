#!/usr/bin/env python3
"""
Sector & Peer Comparison Analysis
Compares stock performance to sector ETF and market
"""
import yfinance as yf
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_sector_comparison(ticker, sector_etf="XLK", peers=None, start="2020-01-01", end=None):
    if end is None:
        end = datetime.now().strftime('%Y-%m-%d')
    """
    Compare stock to sector ETF and optional peers
    sector_etf: XLK=Tech, XLF=Financial, XLE=Energy, XLV=Health, etc.
    """
    print(f"\n{'='*70}")
    print(f"SECTOR & PEER COMPARISON: {ticker}")
    print(f"{'='*70}")
    
    # Fetch stock data
    stock = yf.download(ticker, start=start, progress=False)['Close']
    sector = yf.download(sector_etf, start=start, progress=False)['Close']
    
    if isinstance(stock, pd.DataFrame):
        stock = stock.iloc[:, 0]
    if isinstance(sector, pd.DataFrame):
        sector = sector.iloc[:, 0]
    
    # Calculate returns
    stock_returns = stock.pct_change().dropna()
    sector_returns = sector.pct_change().dropna()
    
    # Align dates
    aligned = pd.concat([stock_returns, sector_returns], axis=1, join='inner')
    aligned.columns = [ticker, sector_etf]
    
    # Performance metrics
    stock_total = (stock.iloc[-1] / stock.iloc[0] - 1) * 100
    sector_total = (sector.iloc[-1] / sector.iloc[0] - 1) * 100
    
    stock_vol = stock_returns.std() * np.sqrt(252) * 100
    sector_vol = sector_returns.std() * np.sqrt(252) * 100
    
    stock_sharpe = (stock_returns.mean() / stock_returns.std()) * np.sqrt(252)
    sector_sharpe = (sector_returns.mean() / sector_returns.std()) * np.sqrt(252)
    
    # Correlation
    correlation = aligned[ticker].corr(aligned[sector_etf])
    
    # Relative strength (stock return / sector return)
    relative_strength = stock_total / sector_total if sector_total != 0 else 0
    
    # Beta to sector
    cov_matrix = aligned.cov()
    beta_to_sector = cov_matrix.iloc[0, 1] / sector_returns.var()
    
    # Output
    print(f"\nPERFORMANCE COMPARISON (since {start}):")
    print(f"\n{'Metric':<25} {ticker:<15} {sector_etf:<15} {'Ratio':>10}")
    print(f"{'-'*70}")
    print(f"{'Total Return':<25} {stock_total:>14.2f}% {sector_total:>14.2f}% {stock_total/sector_total if sector_total else 0:>10.2f}x")
    print(f"{'Annualized Volatility':<25} {stock_vol:>14.2f}% {sector_vol:>14.2f}% {stock_vol/sector_vol:>10.2f}x")
    print(f"{'Sharpe Ratio':<25} {float(stock_sharpe):>14.2f} {float(sector_sharpe):>14.2f} {float(stock_sharpe/sector_sharpe):>10.2f}x")
    
    print(f"\nRELATIONSHIP TO SECTOR:")
    print(f"  Correlation to {sector_etf}: {correlation:.3f}")
    print(f"  Beta to Sector: {beta_to_sector:.2f}")
    print(f"  Relative Strength: {relative_strength:.2f}x")
    
    # Interpretation
    print(f"\nINTERPRETATION:")
    if relative_strength > 1.2:
        assessment = f"STRONG OUTPERFORMER vs {sector_etf} - Leadership position"
    elif relative_strength > 1.0:
        assessment = f"Moderate outperformance vs {sector_etf}"
    elif relative_strength > 0.8:
        assessment = f"In-line performance vs {sector_etf}"
    else:
        assessment = f"UNDERPERFORMER vs {sector_etf} - Lagging sector"
    print(f"  {assessment}")
    
    if correlation > 0.8:
        print(f"  HIGH correlation ({correlation:.2f}) - Stock moves with sector")
    elif correlation > 0.5:
        print(f"  MODERATE correlation ({correlation:.2f}) - Some idiosyncratic movement")
    else:
        print(f"  LOW correlation ({correlation:.2f}) - Stock trades on its own fundamentals")
    
    # Peer comparison if provided
    if peers:
        print(f"\nPEER COMPARISON:")
        peer_data = {}
        for peer in peers:
            try:
                p = yf.download(peer, start=start, progress=False)['Close']
                if isinstance(p, pd.DataFrame):
                    p = p.iloc[:, 0]
                peer_total = (p.iloc[-1] / p.iloc[0] - 1) * 100
                peer_data[peer] = peer_total
            except:
                pass
        
        if peer_data:
            sorted_peers = sorted(peer_data.items(), key=lambda x: x[1], reverse=True)
            print(f"  {'Rank':<6} {'Peer':<10} {'Return':>10}")
            print(f"  {'-'*30}")
            for i, (peer, ret) in enumerate(sorted_peers, 1):
                marker = " ←" if peer == ticker else ""
                print(f"  {i:<6} {peer:<10} {ret:>9.2f}%{marker}")
    
    # Regime detection
    print(f"\nMARKET REGIME DETECTION:")
    spy = yf.download("SPY", start=start, progress=False)['Close']
    if isinstance(spy, pd.DataFrame):
        spy = spy.iloc[:, 0]
    spy_ma200 = spy.rolling(200).mean()
    
    if spy.iloc[-1] > spy_ma200.iloc[-1]:
        regime = "BULL MARKET (SPY above 200 MA)"
    else:
        regime = "BEAR MARKET (SPY below 200 MA)"
    print(f"  Current: {regime}")
    
    spy_vol = spy.pct_change().rolling(20).std().iloc[-1] * np.sqrt(252) * 100
    if spy_vol > 30:
        vol_regime = "HIGH VOLATILITY regime"
    elif spy_vol > 20:
        vol_regime = "MODERATE VOLATILITY regime"
    else:
        vol_regime = "LOW VOLATILITY regime"
    print(f"  Volatility: {vol_regime} (SPY vol: {spy_vol:.1f}%)")
    
    print(f"\n{'='*70}\n")
    
    return {
        'relative_strength': relative_strength,
        'correlation': correlation,
        'beta_to_sector': beta_to_sector
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sector & peer comparison analysis")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--sector", default="XLK", help="Sector ETF (XLK, XLF, XLE, etc.)")
    parser.add_argument("--peers", nargs="*", help="Peer tickers for comparison")
    parser.add_argument("--start", default="2020-01-01", help="Start date")
    args = parser.parse_args()
    
    analyze_sector_comparison(args.ticker, args.sector, args.peers, args.start)
