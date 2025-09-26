#!/usr/bin/env python3
"""
Test the fixed sentiment analyzer
"""

import sys
import os
sys.path.append('/home/ubuntu/Btock')

def test_fixed_sentiment_analyzer():
    """Test the fixed sentiment analyzer"""
    
    print("🧪 Testing Fixed Sentiment Analyzer...")
    
    try:
        from modules.sentiment_analyzer import SentimentAnalyzer
        print("✅ Import successful")
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        print("✅ Initialization successful")
        
        # Check API status
        status = analyzer.get_api_status()
        print(f"✅ API Status: {status}")
        
        # Test with a small ticker list
        test_tickers = ["AAPL", "TSLA"]
        print(f"🚀 Testing sentiment analysis for: {test_tickers}")
        
        # Run sentiment analysis
        results = analyzer.get_sentiment_for_tickers(test_tickers, hours_back=24)
        print(f"✅ Analysis completed. Results shape: {results.shape}")
        
        # Format results
        formatted = analyzer.format_sentiment_results(results)
        print("✅ Results formatted successfully")
        
        # Display results
        print("\n📊 Sample Results:")
        print(formatted.to_string(index=False))
        
        print("\n🎉 Fixed sentiment analyzer test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_sentiment_analyzer()
    if not success:
        sys.exit(1)
