#!/usr/bin/env python3
"""
Test the Reddit data fetching fix
"""

import sys
import os
from datetime import datetime, timezone, timedelta
sys.path.append('/home/ubuntu/Btock')

def test_reddit_data_fetching():
    """Test the Reddit data fetching fix"""
    
    print("🧪 Testing Reddit Data Fetching Fix...")
    
    # Set up environment variables
    os.environ["REDDIT_CLIENT_ID"] = "D14b1bj_bpv_bwtX1KcmA"
    os.environ["REDDIT_CLIENT_SECRET"] = "1DPZmKRSmPOfcxzLgiXVeQChaow"
    os.environ["user_agent"] = "StockResearchBot/1.0"
    
    try:
        from modules.sentiment_analyzer import SentimentAnalyzer
        print("✅ Import successful")
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        print("✅ Initialization successful")
        
        # Check Reddit API status
        status = analyzer.get_api_status()
        print(f"✅ API Status: {status}")
        
        if status.get("Reddit", False):
            print("🚀 Reddit API is working! Testing data fetching...")
            
            # Test Reddit sentiment for a popular stock
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)
            
            test_ticker = "AAPL"
            print(f"\n🔍 Testing Reddit sentiment for {test_ticker}...")
            
            reddit_score = analyzer._get_reddit_sentiment(test_ticker, start_time, end_time)
            
            print(f"\n📊 Results:")
            print(f"   Ticker: {test_ticker}")
            print(f"   Reddit Sentiment Score: {reddit_score}")
            print(f"   Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
            
            if reddit_score != 0:
                print("✅ SUCCESS: Reddit is now returning real sentiment data!")
            else:
                print("⚠️  Reddit returned 0 - this might be normal if no posts found in timeframe")
                
            # Test another popular ticker
            test_ticker2 = "TSLA"
            print(f"\n🔍 Testing Reddit sentiment for {test_ticker2}...")
            reddit_score2 = analyzer._get_reddit_sentiment(test_ticker2, start_time, end_time)
            print(f"   {test_ticker2} Reddit Score: {reddit_score2}")
            
            if reddit_score != 0 or reddit_score2 != 0:
                print("\n🎉 Reddit data fetching is working correctly!")
                return True
            else:
                print("\n⚠️  Both tickers returned 0 - may need to adjust search parameters")
                return False
                
        else:
            print("❌ Reddit API not configured - cannot test data fetching")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_reddit_data_fetching()
    if not success:
        sys.exit(1)
