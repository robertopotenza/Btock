#!/usr/bin/env python3
"""
Test the production sentiment analyzer (no demo mode)
"""

import sys
import os
sys.path.append('/home/ubuntu/Btock')

def test_production_sentiment_analyzer():
    """Test the production sentiment analyzer"""
    
    print("🧪 Testing Production Sentiment Analyzer...")
    
    try:
        from modules.sentiment_analyzer import SentimentAnalyzer
        print("✅ Import successful")
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        print("✅ Initialization successful")
        
        # Check API status
        status = analyzer.get_api_status()
        print(f"✅ API Status: {status}")
        
        # Check if any APIs are configured
        working_apis = [name for name, configured in status.items() if configured]
        
        if working_apis:
            print(f"🚀 Configured APIs: {', '.join(working_apis)}")
            
            # Test with a small ticker list
            test_tickers = ["AAPL"]
            print(f"🚀 Testing sentiment analysis for: {test_tickers}")
            
            # Run sentiment analysis
            results = analyzer.get_sentiment_for_tickers(test_tickers, hours_back=24)
            
            if not results.empty:
                print(f"✅ Analysis completed. Results shape: {results.shape}")
                
                # Format results
                formatted = analyzer.format_sentiment_results(results)
                print("✅ Results formatted successfully")
                
                # Display results
                print("\n📊 Sample Results:")
                print(formatted.to_string(index=False))
                
                print("\n🚀 Production sentiment analyzer working with real APIs!")
            else:
                print("⚠️ No results returned - APIs may need configuration")
        else:
            print("⚠️ No APIs configured - this will show setup guidance to users")
            print("   - Set XAI_API_KEY for X (Twitter) sentiment")
            print("   - Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET for Reddit sentiment")
            print("   - StockTwits works without configuration (public API)")
        
        print("\n🎉 Production sentiment analyzer test COMPLETED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_production_sentiment_analyzer()
    if not success:
        sys.exit(1)
