#!/usr/bin/env python3
"""
Test the X API troubleshooting and fixes
"""

import sys
import os
import requests
from datetime import datetime, timezone, timedelta
sys.path.append('/home/ubuntu/Btock')

def test_x_api_manually():
    """Test X API manually with different endpoints"""
    
    print("🧪 Testing X API Endpoints Manually...")
    
    # Use the API key from Railway environment
    api_key = "xai-D2gvIxMfaNn9kzadd4JvxL632GAGz5nHaO4DqbQy3cn1E23qaQDcvOcdhxURf"
    
    endpoints_to_test = [
        "https://api.x.ai/v1/chat/completions",      # Current
        "https://api.x.ai/v1/completions",           # Alternative 1
        "https://grok.x.ai/v1/chat/completions",     # Alternative 2
        "https://api.openai.com/v1/chat/completions" # OpenAI fallback
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "grok-beta",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 1
    }
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS: Endpoint working!")
                print(f"   Response: {response.json()}")
                return endpoint
            elif response.status_code == 404:
                print(f"   ❌ 404 Not Found: Endpoint doesn't exist")
            elif response.status_code == 401:
                print(f"   ❌ 401 Unauthorized: Invalid API key")
            elif response.status_code == 403:
                print(f"   ❌ 403 Forbidden: Access denied")
            else:
                print(f"   ⚠️  {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout: Endpoint not responding")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error: Cannot reach endpoint")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ No working X API endpoints found")
    return None

def test_sentiment_analyzer():
    """Test the sentiment analyzer with X API"""
    
    print("\n🧪 Testing Sentiment Analyzer with X API...")
    
    # Set up environment variables
    os.environ["XAI_API_KEY"] = "xai-D2gvIxMfaNn9kzadd4JvxL632GAGz5nHaO4DqbQy3cn1E23qaQDcvOcdhxURf"
    os.environ["XAI_API_URL"] = "https://api.x.ai/v1/chat/completions"
    
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
    
    print("🔧 X API 404 Error Troubleshooting Test")
    print("=" * 50)
    
    # Test 1: Manual API endpoint testing
    working_endpoint = test_x_api_manually()
    
    if working_endpoint:
        print(f"\n✅ Found working endpoint: {working_endpoint}")
        print(f"💡 Update XAI_API_URL in Railway to: {working_endpoint}")
        
        # Update environment for testing
        os.environ["XAI_API_URL"] = working_endpoint
        
        # Test 2: Sentiment analyzer testing
        success = test_sentiment_analyzer()
        
        if success:
            print("\n🎉 X API troubleshooting successful!")
            print(f"🚀 Use this endpoint in Railway: {working_endpoint}")
        else:
            print("\n⚠️  X API endpoint works but sentiment analysis needs adjustment")
    else:
        print("\n❌ No working X API endpoints found")
        print("💡 Recommendations:")
        print("   1. Check Grok API subscription at https://x.ai/")
        print("   2. Verify API key is valid and active")
        print("   3. Try using OpenAI API instead")
        print("   4. Disable X sentiment temporarily")

if __name__ == "__main__":
    main()
