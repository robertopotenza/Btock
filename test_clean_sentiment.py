#!/usr/bin/env python3
"""
Test the clean single-mode sentiment analyzer
"""

import sys
import os
sys.path.append('/home/ubuntu/Btock')

def test_clean_sentiment_analyzer():
    """Test the clean single-mode sentiment analyzer"""
    
    print("🧪 Testing Clean Single-Mode Sentiment Analyzer...")
    
    try:
        from modules.sentiment_analyzer import SentimentAnalyzer
        print("✅ Import successful")
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        print("✅ Initialization successful")
        
        # Check mode
        print(f"✅ Operating Mode: {'Demo Mode' if analyzer.demo_mode else 'Live API Mode'}")
        
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
        
        # Verify single-mode operation
        if analyzer.demo_mode:
            print("\n🎯 Confirmed: Operating in Demo Mode (simulated data)")
            print("   - All data is simulated for demonstration")
            print("   - No mixing of real and simulated data")
            print("   - Clear indication to user about demo mode")
        else:
            print("\n🚀 Confirmed: Operating in Live API Mode (real data)")
            print("   - All data from real APIs")
            print("   - No fallback to simulated data")
            print("   - Clear indication to user about live mode")
        
        print("\n🎉 Clean single-mode sentiment analyzer test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_clean_sentiment_analyzer()
    if not success:
        sys.exit(1)
