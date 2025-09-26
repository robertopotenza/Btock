"""
Simple test script for Btock without Streamlit dependencies
"""

import yfinance as yf
import ta
import pandas as pd
import numpy as np

def test_simple():
    print("🧪 Testing Core Functionality")
    print("=" * 40)
    
    # Test data fetching
    print("1. Testing data fetch...")
    ticker = "AAPL"
    stock = yf.Ticker(ticker)
    data = stock.history(period="6mo")
    
    if data.empty:
        print("❌ Failed to fetch data")
        return False
    
    print(f"✅ Fetched {len(data)} days of data")
    print(f"📊 Latest close: ${data['Close'].iloc[-1]:.2f}")
    
    # Test basic indicators
    print("\n2. Testing indicators...")
    
    try:
        # RSI
        rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        print(f"📈 RSI: {rsi.iloc[-1]:.2f}")
        
        # MACD
        macd_indicator = ta.trend.MACD(data['Close'])
        macd = macd_indicator.macd()
        print(f"📈 MACD: {macd.iloc[-1]:.4f}")
        
        # ATR
        atr = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close'], window=14).average_true_range()
        print(f"📈 ATR: {atr.iloc[-1]:.2f}")
        
        # ADX
        adx_indicator = ta.trend.ADXIndicator(data['High'], data['Low'], data['Close'], window=14)
        adx = adx_indicator.adx()
        print(f"📈 ADX: {adx.iloc[-1]:.2f}")
        
        print("✅ All indicators calculated successfully")
        
    except Exception as e:
        print(f"❌ Error calculating indicators: {e}")
        return False
    
    print("\n🎉 Core functionality test passed!")
    return True

if __name__ == "__main__":
    test_simple()
