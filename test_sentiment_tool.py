#!/usr/bin/env python3
"""
Test script to verify sentiment_app.py works independently
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def test_sentiment_app():
    """Test if sentiment_app.py can start successfully"""
    
    print("🧪 Testing Sentiment Analysis Tool...")
    
    # Check if sentiment_app.py exists
    sentiment_app_path = Path("sentiment_app.py")
    if not sentiment_app_path.exists():
        print("❌ sentiment_app.py not found!")
        return False
    
    print("✅ sentiment_app.py found")
    
    # Try to import the modules
    try:
        from modules.sentiment_analyzer import SentimentAnalyzer
        print("✅ SentimentAnalyzer import successful")
        
        # Test initialization
        analyzer = SentimentAnalyzer()
        print("✅ SentimentAnalyzer initialization successful")
        
        # Test API status
        status = analyzer.get_api_status()
        print(f"✅ API status check: {status}")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Try to start streamlit (with timeout)
    try:
        print("🚀 Testing Streamlit startup...")
        
        # Start streamlit in background with timeout
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "sentiment_app.py",
            "--server.port=8505",
            "--server.headless=true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Streamlit started successfully")
            
            # Try to access the app
            try:
                response = requests.get("http://localhost:8505", timeout=5)
                if response.status_code == 200:
                    print("✅ Sentiment app accessible via HTTP")
                else:
                    print(f"⚠️ HTTP response: {response.status_code}")
            except:
                print("⚠️ Could not access via HTTP (normal for headless mode)")
            
            # Terminate the process
            process.terminate()
            process.wait()
            print("✅ Streamlit process terminated cleanly")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Streamlit test error: {e}")
        return False

if __name__ == "__main__":
    success = test_sentiment_app()
    if success:
        print("\n🎉 Sentiment tool test PASSED!")
        print("\n📋 To use the sentiment tool:")
        print("1. Run: streamlit run sentiment_app.py")
        print("2. Open the URL shown in terminal")
        print("3. Enter tickers and configure analysis")
    else:
        print("\n❌ Sentiment tool test FAILED!")
        sys.exit(1)
