#!/usr/bin/env python3
import yfinance as yf
import argparse
import re
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data
from datetime import datetime

def fetch_data(ticker, start="2025-01-01", end=None):
    # Validate ticker to prevent path traversal
    if not isinstance(ticker, str) or not re.match(r'^[A-Z]{1,5}$', ticker.upper()):
        raise ValueError(f"Invalid ticker: '{ticker}'. Must be 1-5 uppercase letters.")
    ticker = ticker.upper()

    if end is None:
        end = datetime.now().strftime('%Y-%m-%d')
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}")

    # Flatten MultiIndex columns (yfinance compat)
    df = flatten_yf_data(df)
    # Validate output path is safe (no path traversal)
    safe_ticker = re.sub(r'[^A-Za-z0-9]', '_', ticker)
    output_path = f"{safe_ticker}_data.csv"
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
