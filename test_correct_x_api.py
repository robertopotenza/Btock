#!/usr/bin/env python3
"""
Test the correct X API integration
"""

import sys
import os
import requests
from datetime import datetime, timezone, timedelta
sys.path.append('/home/ubuntu/Btock')

def test_correct_x_api():
    """Test the correct X API configuration"""
    
    print("🧪 Testing Correct X API Integration...")
    
    # Use the correct X API configuration
    api_key = "xai-D2gvIxMfaNn9kzadd4JvxL632GAGz5nHaO4DqbQy3cn1E23qaQDcvOcdhxURf"
    api_url = "https://api.x.ai/v1/messages"
    model = "grok-3"
    
    print(f"🔍 Testing Configuration:")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   API URL: {api_url}")
    print(f"   Model: {model}")
    
    # Test the API manually first
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "user", "content": "Analyze recent X posts about $AAPL stock. Count positive vs negative sentiment mentions. Return format: 'positive: X, negative: Y'"}]
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    try:
        print(f"\n🚀 Making direct API request...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: API working!")
            print(f"   Response: {data}")
            
            # Test response parsing
            if "content" in data and len(data["content"]) > 0:
                content = data["content"][0]["text"]
                print(f"   Content: {content}")
                return True
            else:
                print(f"   ⚠️  Unexpected response format: {data}")
                return False
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_sentiment_analyzer_integration():
    """Test the sentiment analyzer with correct X API"""
    
    print("\n🧪 Testing Sentiment Analyzer Integration...")
    
    # Set up environment variables with correct configuration
    os.environ["XAI_API_KEY"] = "xai-D2gvIxMfaNn9kzadd4JvxL632GAGz5nHaO4DqbQy3cn1E23qaQDcvOcdhxURf"
    os.environ["XAI_API_URL"] = "https://api.x.ai/v1/messages"
    os.environ["XAI_MODEL"] = "grok-3"
    
    try:
        from modules.sentiment_analyzer import SentimentAnalyzer
        print("✅ Import successful")
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        print("✅ Initialization successful")
        
        # Check X API status
        status = analyzer.get_api_status()
        print(f"✅ API Status: {status}")
        
        if status.get("X (Grok API)", False):
            print("🚀 X API is configured! Testing sentiment analysis...")
            
            # Test X sentiment for a ticker
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)
            
            test_ticker = "AAPL"
            print(f"\n🔍 Testing X sentiment for {test_ticker}...")
            
            x_score = analyzer._get_x_sentiment(test_ticker, start_time, end_time)
            
            print(f"\n📊 Results:")
            print(f"   Ticker: {test_ticker}")
            print(f"   X Sentiment Score: {x_score}")
            
            if x_score != 0:
                print("✅ SUCCESS: X API is working and returning sentiment data!")
                return True
            else:
                print("⚠️  X API returned 0 - check the detailed logs above")
                return False
                
        else:
            print("❌ X API not configured or not working")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print("🔧 Correct X API Integration Test")
    print("=" * 50)
    
    # Test 1: Direct API testing
    api_success = test_correct_x_api()
    
    if api_success:
        print("\n✅ Direct API test successful!")
        
        # Test 2: Sentiment analyzer integration
        integration_success = test_sentiment_analyzer_integration()
        
        if integration_success:
            print("\n🎉 X API integration successful!")
            print("🚀 Update Railway variables:")
            print("   XAI_API_URL=https://api.x.ai/v1/messages")
            print("   XAI_MODEL=grok-3")
        else:
            print("\n⚠️  Integration needs adjustment")
    else:
        print("\n❌ Direct API test failed - check API key and configuration")

if __name__ == "__main__":
    main()
