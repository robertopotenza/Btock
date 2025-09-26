#!/usr/bin/env python3
"""
Simple launcher for the Sentiment Analysis Tool
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def launch_sentiment_tool():
    """Launch the sentiment analysis tool"""
    
    print("🚀 Launching Btock Sentiment Analysis Tool...")
    
    # Check if sentiment_app.py exists
    if not Path("sentiment_app.py").exists():
        print("❌ Error: sentiment_app.py not found!")
        print("Make sure you're in the Btock directory.")
        return False
    
    try:
        # Start streamlit
        print("📊 Starting Streamlit server...")
        
        # Use a different port to avoid conflicts
        port = 8506
        
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "sentiment_app.py",
            f"--server.port={port}",
            "--server.address=0.0.0.0"
        ])
        
        print(f"✅ Sentiment Analysis Tool started!")
        print(f"🌐 Access at: http://localhost:{port}")
        print(f"🔗 Network URL: http://0.0.0.0:{port}")
        print("\n📋 Instructions:")
        print("1. Open the URL above in your browser")
        print("2. Enter tickers manually or upload a file")
        print("3. Configure time range for analysis")
        print("4. Run sentiment analysis")
        print("\n⚠️ Press Ctrl+C to stop the server")
        
        # Wait for the process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping sentiment analysis tool...")
            process.terminate()
            process.wait()
            print("✅ Sentiment tool stopped.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error launching sentiment tool: {e}")
        return False

if __name__ == "__main__":
    launch_sentiment_tool()
