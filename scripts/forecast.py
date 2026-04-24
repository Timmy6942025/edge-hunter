#!/usr/bin/env python3
"""
Forecasting Engine - Professional Grade
Uses Prophet for time series forecasting.
Removes simplistic BUY/SELL recommendations - provides data only.
Let master_analysis.py synthesize the recommendation.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from prophet import Prophet
import argparse
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data
from datetime import datetime

def validate_ticker(ticker):
    """Validate ticker format to prevent path traversal/injection."""
    if not isinstance(ticker, str) or not re.match(r'^[A-Z]{1,5}$', ticker.upper()):
        raise ValueError(f"Invalid ticker: '{ticker}'. Must be 1-5 uppercase letters.")
    return ticker.upper()

def calculate_technical_indicators(df):
    """Add technical indicators - NO look-ahead bias"""
    df = df.copy()
    close = df['Close']

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df['BB_middle'] = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)

    # Moving Averages
    df['SMA_50'] = close.rolling(window=50).mean()
    df['SMA_200'] = close.rolling(window=200).mean()
    df['EMA_12'] = close.ewm(span=12, adjust=False).mean()

    return df

def forecast_stock(ticker, periods=30):
    """Professional-grade forecast using Prophet"""
    ticker = validate_ticker(ticker)
    end_date = datetime.now().strftime('%Y-%m-%d')

    # Fetch extended history for better training
    df = yf.download(ticker, start="2018-01-01", end=end_date, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")

    # Flatten MultiIndex columns (yfinance compat)
    df = flatten_yf_data(df)

    # Calculate technical indicators
    df = calculate_technical_indicators(df)

    # Prepare data for Prophet
    prophet_df = df[["Close"]].reset_index()
    prophet_df.columns = ["ds", "y"]

    # Prophet model with reasonable parameters
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )
    model.fit(prophet_df)

    # Create future dataframe
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    # Current metrics
    current_price = float(df['Close'].iloc[-1])
    prophet_forecast_price = float(forecast['yhat'].iloc[-1])
    prophet_change = ((prophet_forecast_price - current_price) / current_price) * 100

    # Uncertainty quantification
    yhat_lower = float(forecast['yhat_lower'].iloc[-1])
    yhat_upper = float(forecast['yhat_upper'].iloc[-1])
    uncertainty_range = ((yhat_upper - yhat_lower) / yhat_lower) * 100

    # Technical indicators (latest values)
    latest = df.iloc[-1]
    rsi = float(latest['RSI'])
    macd = float(latest['MACD'])
    macd_signal = float(latest['MACD_Signal'])
    sma_50 = float(latest['SMA_50'])
    sma_200 = float(latest['SMA_200'])

    # Save detailed forecast (validate path)
    safe_ticker = re.sub(r'[^A-Za-z0-9]', '_', ticker)
    output_path = f"{safe_ticker}_forecast.csv"
    forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv(output_path, index=False)

    # Output disciplined analysis (NO fake recommendations)
    print(f"\n{'='*70}")
    print(f"FORECASTING ENGINE: {ticker}")
    print(f"CURRENT DATE: {end_date}")
    print(f"{'='*70}")

    print(f"\nPROPHET FORECAST ({periods} days):")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"  Forecast Price: ${prophet_forecast_price:.2f}")
    print(f"  Expected Change: {prophet_change:+.2f}%")
    print(f"  95% Confidence Interval: ${yhat_lower:.2f} - ${yhat_upper:.2f}")
    print(f"  Uncertainty Range: ±{uncertainty_range:.1f}%")

    print(f"\nTECHNICAL INDICATORS (Latest):")
    print(f"  RSI (14): {rsi:.2f} {'(Overbought)' if rsi > 70 else '(Oversold)' if rsi < 30 else '(Neutral)'}")
    print(f"  MACD: {macd:.4f} (Signal: {macd_signal:.4f})")
    print(f"  SMA 50: ${sma_50:.2f} {'(Price > SMA50)' if current_price > sma_50 else '(Price < SMA50)'}")
    print(f"  SMA 200: ${sma_200:.2f} {'(Price > SMA200)' if current_price > sma_200 else '(Price < SMA200)'}")
    print(f"  BB Upper: ${float(latest['BB_upper']):.2f}")
    print(f"  BB Lower: ${float(latest['BB_lower']):.2f}")
    bb_range = float(latest['BB_upper']) - float(latest['BB_lower'])
    bb_pos = ((current_price - float(latest['BB_lower'])) / bb_range * 100) if bb_range > 0 else 0
    print(f"  Price vs BB: {bb_pos:.1f}% between bands")

    # Trend analysis
    sma_50_slope = (
        ((df['SMA_50'].iloc[-1] - df['SMA_50'].iloc[-5])
         / df['SMA_50'].iloc[-5]) * 100
        if len(df) >= 5 else 0
    )
    trend = "UP" if sma_50_slope > 0 else "DOWN"
    print(f"\nTREND ANALYSIS:")
    print(f"  SMA 50 Slope (5-day): {sma_50_slope:+.2f}% → {trend}")
    print(f"  Price vs SMA 50: {((current_price/sma_50 - 1)*100):+.2f}%")
    print(f"  Price vs SMA 200: {((current_price/sma_200 - 1)*100):+.2f}%")

    print(f"\n{'='*70}")
    print(f"DATA OUTPUT (for master_analysis.py synthesis):")
    print(f"  prophet_change_pct: {prophet_change:.2f}")
    print(f"  rsi: {rsi:.2f}")
    print(f"  macd_vs_signal: {macd - macd_signal:+.4f}")
    print(f"  trend: {trend}")
    print(f"  uncertainty_range_pct: {uncertainty_range:.1f}")
    print(f"{'='*70}\n")

    return {
        "current_price": current_price,
        "forecast_price": prophet_forecast_price,
        "change_pct": prophet_change,
        "uncertainty_pct": uncertainty_range,
        "rsi": rsi,
        "macd": macd,
        "trend": trend
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Professional forecasting with Prophet (no fake recommendations)")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--periods", type=int, default=30, help="Days to forecast")
    args = parser.parse_args()
    try:
        forecast_stock(args.ticker, args.periods)
    except ValueError as e:
        print(f"Input error: {e}")
    except Exception as e:
        print(f"Forecast error: {type(e).__name__} - {e}")
