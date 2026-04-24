#!/usr/bin/env python3
"""
News Sentiment Analysis (Free, No API Key)
Uses yfinance news aggregation for basic sentiment scoring
"""
import yfinance as yf
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import flatten_yf_data, extract_price_data, safe_float
from datetime import datetime

def analyze_news_sentiment(ticker):
    """Analyze recent news sentiment from yfinance"""
    print(f"\n{'='*70}")
    print(f"NEWS SENTIMENT ANALYSIS: {ticker}")
    print(f"{'='*70}")
    
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news or len(news) == 0:
            print(f"\nNo recent news found for {ticker}")
            return
        
        # Sentiment keywords
        bullish_words = ['beat', 'strong', 'surge', 'gain', 'profit', 'growth', 'upgrade', 
                        'bullish', 'outperform', 'buy', 'positive', 'record', 'jump']
        bearish_words = ['miss', 'weak', 'dropped', 'loss', 'decline', 'downgrade', 
                        'bearish', 'underperform', 'sell', 'negative', 'plunge', 'risk']
        
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        print(f"\nRECENT NEWS (Last {min(10, len(news))} articles):")
        print(f"{'Date':<12} {'Sentiment':<10} {'Title'}")
        print(f"{'-'*70}")
        
        for i, article in enumerate(news[:10]):
            title = article.get('title', '')
            ts = article.get('providerPublishTime', 0)
            if ts > 0:
                pub_date = datetime.fromtimestamp(ts)
                date_str = pub_date.strftime('%Y-%m-%d')
            else:
                date_str = 'N/A'
            
            # Simple sentiment scoring
            title_lower = title.lower()
            bullish_score = sum(1 for word in bullish_words if word in title_lower)
            bearish_score = sum(1 for word in bearish_words if word in title_lower)
            
            if bullish_score > bearish_score:
                sentiment = "BULLISH"
                bullish_count += 1
            elif bearish_score > bullish_score:
                sentiment = "BEARISH"
                bearish_count += 1
            else:
                sentiment = "NEUTRAL"
                neutral_count += 1
            
            print(f"{date_str:<12} {sentiment:<10} {title[:60]}")
        
        total = bullish_count + bearish_count + neutral_count
        bullish_pct = (bullish_count / total) * 100 if total > 0 else 0
        bearish_pct = (bearish_count / total) * 100 if total > 0 else 0
        
        print(f"\nSENTIMENT SUMMARY:")
        print(f"  Bullish: {bullish_count} ({bullish_pct:.0f}%)")
        print(f"  Bearish: {bearish_count} ({bearish_pct:.0f}%)")
        print(f"  Neutral: {neutral_count} ({100-bullish_pct-bearish_pct:.0f}%)")
        
        # Overall sentiment
        if bullish_pct > 60:
            overall = "VERY BULLISH - Strong positive sentiment"
        elif bullish_pct > 40:
            overall = "MODERATELY BULLISH - Positive sentiment"
        elif bearish_pct > 60:
            overall = "VERY BEARISH - Strong negative sentiment"
        elif bearish_pct > 40:
            overall = "MODERATELY BEARISH - Negative sentiment"
        else:
            overall = "NEUTRAL - Mixed sentiment"
        
        print(f"\nOVERALL SENTIMENT: {overall}")
        
        # Compare to RSI for divergence
        print(f"\nSENTIMENT VS PRICE DIVERGENCE CHECK:")
        print(f"  If sentiment bullish but RSI > 70: Potential bull trap")
        print(f"  If sentiment bearish but RSI < 30: Potential bear trap")
        print(f"  Aligned sentiment + RSI: Higher conviction setup")
        
    except Exception as e:
        print(f"\nNews sentiment error: {e}")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="News sentiment analysis (free, no API key)")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    args = parser.parse_args()
    analyze_news_sentiment(args.ticker)
