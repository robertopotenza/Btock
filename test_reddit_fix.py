#!/usr/bin/env python3
"""
Test the Reddit API fix for user agent environment variable
"""

import sys
import os
sys.path.append('/home/ubuntu/Btock')

def test_reddit_api_fix():
    """Test the Reddit API fix"""
    
    print("🧪 Testing Reddit API Fix...")
    
    # Simulate the environment variables from Railway
    os.environ["REDDIT_CLIENT_ID"] = "D14b1bj_bpv_bwtX1KcmA"
    os.environ["REDDIT_CLIENT_SECRET"] = "1DPZmKRSmPOfcxzLgiXVeQChaow"
    os.environ["user_agent"] = "StockResearchBot/1.0"  # This is what's in Railway
    
    try:
        from modules.sentiment_analyzer import SentimentAnalyzer
        print("✅ Import successful")
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        print("✅ Initialization successful")
        
        # Check Reddit API status
        status = analyzer.get_api_status()
        print(f"✅ API Status: {status}")
        
        # Check if Reddit is configured
        if status.get("Reddit", False):
            print("🚀 Reddit API configured successfully!")
            print(f"   - Client ID: {os.getenv('REDDIT_CLIENT_ID')}")
            print(f"   - User Agent: {os.getenv('user_agent') or os.getenv('REDDIT_USER_AGENT')}")
            
            # Test Reddit sentiment (quick test)
            print("🧪 Testing Reddit sentiment analysis...")
            from datetime import datetime, timezone, timedelta
            
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)
            
            reddit_score = analyzer._get_reddit_sentiment("AAPL", start_time, end_time)
            print(f"✅ Reddit sentiment test completed. Score: {reddit_score}")
            
        else:
            print("❌ Reddit API still not configured")
            
        print("\n🎉 Reddit API fix test COMPLETED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_reddit_api_fix()
    if not success:
        sys.exit(1)
