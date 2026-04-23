#!/usr/bin/env python3
import pandas as pd
import numpy as np
import yfinance as yf
from prophet import Prophet
import argparse
from datetime import datetime, timedelta

def calculate_technical_indicators(df):
    """Add technical indicators to the dataframe"""
    df = df.copy()
    
    # Handle MultiIndex columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
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
    # Fetch extended history for better training
    end_date = datetime.now().strftime('%Y-%m-%d')
    df = yf.download(ticker, start="2018-01-01", end=end_date, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")
    
    # Calculate technical indicators
    df = calculate_technical_indicators(df)
    
    # Prophet Forecast
    prophet_df = df[["Close"]].reset_index()
    prophet_df.columns = ["ds", "y"]
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        yearly_seasonality=True,
        weekly_seasonality=True
    )
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    current_price = df['Close'].iloc[-1]
    prophet_forecast_price = forecast['yhat'].iloc[-1]
    prophet_change = ((prophet_forecast_price - current_price) / current_price) * 100
    
    # Technical Signal
    latest = df.iloc[-1]
    signals = []
    
    # RSI Signal
    if latest['RSI'] < 30:
        signals.append("RSI_OVERSOLD (BUY signal)")
    elif latest['RSI'] > 70:
        signals.append("RSI_OVERBOUGHT (SELL signal)")
    
    # MACD Signal
    if latest['MACD'] > latest['MACD_Signal']:
        signals.append("MACD_BULLISH_CROSSOVER")
    elif latest['MACD'] < latest['MACD_Signal']:
        signals.append("MACD_BEARISH_CROSSOVER")
    
    # Moving Average Signal
    if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
        signals.append("STRONG_UPTREND (Price > SMA50 > SMA200)")
    elif latest['Close'] < latest['SMA_50'] < latest['SMA_200']:
        signals.append("STRONG_DOWNTREND (Price < SMA50 < SMA200)")
    
    # Bollinger Bands Signal
    if latest['Close'] < latest['BB_lower']:
        signals.append("BELOW_BB_LOWER (Potential BUY)")
    elif latest['Close'] > latest['BB_upper']:
        signals.append("ABOVE_BB_UPPER (Potential SELL)")
    
    # Trend Analysis
    sma_50_slope = (df['SMA_50'].iloc[-1] - df['SMA_50'].iloc[-5]) / df['SMA_50'].iloc[-5] * 100
    trend_direction = "UP" if sma_50_slope > 0 else "DOWN"
    
    # Decision Logic
    bullish_signals = sum(['BUY' in s or 'UNDER' in s or 'UP' in s or 'BULLISH' in s for s in signals])
    bearish_signals = sum(['SELL' in s or 'OVER' in s or 'DOWN' in s or 'BEARISH' in s for s in signals])
    
    if bullish_signals > bearish_signals and prophet_change > 0:
        recommendation = "BUY"
        confidence = "HIGH" if bullish_signals >= 3 else "MEDIUM"
    elif bearish_signals > bullish_signals and prophet_change < 0:
        recommendation = "SELL"
        confidence = "HIGH" if bearish_signals >= 3 else "MEDIUM"
    else:
        recommendation = "HOLD"
        confidence = "MEDIUM"
    
    # Output comprehensive analysis
    print(f"\n{'='*60}")
    print(f"QUANTITATIVE ANALYSIS: {ticker}")
    print(f"{'='*60}")
    print(f"\nCURRENT METRICS:")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"  RSI (14): {latest['RSI']:.2f}")
    print(f"  MACD: {latest['MACD']:.4f}")
    print(f"  SMA 50: ${latest['SMA_50']:.2f}")
    print(f"  SMA 200: ${latest['SMA_200']:.2f}")
    
    print(f"\nPROPHET FORECAST ({periods} days):")
    print(f"  Predicted Price: ${prophet_forecast_price:.2f}")
    print(f"  Expected Change: {prophet_change:+.2f}%")
    
    print(f"\nTECHNICAL SIGNALS:")
    for signal in signals:
        print(f"  • {signal}")
    
    print(f"\nTREND ANALYSIS:")
    print(f"  SMA 50 Slope: {sma_50_slope:+.2f}% (5-day)")
    print(f"  Trend Direction: {trend_direction}")
    
    print(f"\n{'='*60}")
    print(f"RECOMMENDATION: {recommendation}")
    print(f"CONFIDENCE: {confidence}")
    print(f"Bullish Signals: {bullish_signals} | Bearish Signals: {bearish_signals}")
    print(f"{'='*60}\n")
    
    # Save detailed forecast
    output_path = f"{ticker}_comprehensive_forecast.csv"
    forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv(output_path, index=False)
    
    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "current_price": current_price,
        "forecast_price": prophet_forecast_price,
        "change_pct": prophet_change,
        "signals": signals
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deep stock forecasting with technical analysis")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--periods", type=int, default=30, help="Days to forecast")
    args = parser.parse_args()
    forecast_stock(args.ticker, args.periods)
