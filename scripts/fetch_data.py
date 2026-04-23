#!/usr/bin/env python3
import yfinance as yf
import argparse
import os
from datetime import datetime

def fetch_data(ticker, start="2025-01-01", end=None):
    if end is None:
        end = datetime.now().strftime('%Y-%m-%d')
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    output_path = f"{ticker}_data.csv"
    df.to_csv(output_path)
    print(f"Data saved to {output_path}")
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch historical stock data via yfinance (no API key)")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--start", default="2025-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2026-04-23", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    fetch_data(args.ticker, args.start, args.end)
