#!/usr/bin/env python3
"""
Horizontal Scrolling Demo
Simple demonstration of the horizontal scrolling functionality
"""

import streamlit as st
import pandas as pd
import numpy as np

def create_demo_data():
    """Create demo data with many columns to demonstrate horizontal scrolling"""
    np.random.seed(42)
    
    tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 'CRM', 'AMD']
    
    data = {
        'Ticker': tickers,
        'Current Price': np.random.uniform(50, 500, len(tickers)),
        'Final Score': np.random.uniform(-1, 1, len(tickers)),
        'Signal': np.random.choice(['BUY', 'HOLD', 'SELL'], len(tickers)),
        'Momentum': np.random.uniform(-1, 1, len(tickers)),
        'Trend': np.random.uniform(-1, 1, len(tickers)),
        'Volatility': np.random.uniform(-1, 1, len(tickers)),
        'Strength': np.random.uniform(-1, 1, len(tickers)),
        'Support/Resistance': np.random.uniform(-1, 1, len(tickers)),
        'RSI': np.random.uniform(0, 100, len(tickers)),
        'MACD': np.random.uniform(-5, 5, len(tickers)),
        'ATR': np.random.uniform(0, 10, len(tickers)),
        'ADX': np.random.uniform(0, 100, len(tickers)),
        'Stochastic': np.random.uniform(0, 100, len(tickers)),
        'Williams %R': np.random.uniform(-100, 0, len(tickers)),
        'CCI': np.random.uniform(-200, 200, len(tickers)),
        'Volume': np.random.uniform(1000000, 100000000, len(tickers)),
        'Market Cap': np.random.uniform(1e9, 3e12, len(tickers))
    }
    
    df = pd.DataFrame(data)
    
    # Format numeric columns
    df['Current Price'] = df['Current Price'].apply(lambda x: f"${x:.2f}")
    df['Final Score'] = df['Final Score'].apply(lambda x: f"{x:.4f}")
    df['Momentum'] = df['Momentum'].apply(lambda x: f"{x:.4f}")
    df['Trend'] = df['Trend'].apply(lambda x: f"{x:.4f}")
    df['Volatility'] = df['Volatility'].apply(lambda x: f"{x:.4f}")
    df['Strength'] = df['Strength'].apply(lambda x: f"{x:.4f}")
    df['Support/Resistance'] = df['Support/Resistance'].apply(lambda x: f"{x:.4f}")
    df['RSI'] = df['RSI'].apply(lambda x: f"{x:.2f}")
    df['MACD'] = df['MACD'].apply(lambda x: f"{x:.4f}")
    df['ATR'] = df['ATR'].apply(lambda x: f"{x:.2f}")
    df['ADX'] = df['ADX'].apply(lambda x: f"{x:.2f}")
    df['Stochastic'] = df['Stochastic'].apply(lambda x: f"{x:.2f}")
    df['Williams %R'] = df['Williams %R'].apply(lambda x: f"{x:.2f}")
    df['CCI'] = df['CCI'].apply(lambda x: f"{x:.2f}")
    df['Volume'] = df['Volume'].apply(lambda x: f"{x:,.0f}")
    df['Market Cap'] = df['Market Cap'].apply(lambda x: f"${x/1e9:.1f}B")
    
    return df

def main():
    st.set_page_config(
        page_title="Horizontal Scrolling Demo",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Horizontal Scrolling Demo")
    st.markdown("**Demonstration of horizontal scrolling functionality with wide tables**")
    
    # Create demo data
    demo_df = create_demo_data()
    
    st.subheader("🧪 Test Results - Horizontal Scrolling Enabled")
    st.info("This table has 18 columns with a fixed width of 1400px. You should see horizontal scrollbars when the table is wider than your viewport.")
    
    # Display table with horizontal scrolling (same configuration as fixed app.py)
    st.dataframe(
        demo_df,
        width=1400,  # Fixed width to force horizontal scrolling
        height=400,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width=80),
            "Current Price": st.column_config.TextColumn("Current Price", width=100),
            "Final Score": st.column_config.NumberColumn("Final Score", width=100),
            "Signal": st.column_config.TextColumn("Signal", width=80),
            "Momentum": st.column_config.NumberColumn("Momentum", width=100),
            "Trend": st.column_config.NumberColumn("Trend", width=100),
            "Volatility": st.column_config.NumberColumn("Volatility", width=100),
            "Strength": st.column_config.NumberColumn("Strength", width=100),
            "Support/Resistance": st.column_config.NumberColumn("Support/Resistance", width=120),
            "RSI": st.column_config.NumberColumn("RSI", width=80),
            "MACD": st.column_config.NumberColumn("MACD", width=100),
            "ATR": st.column_config.NumberColumn("ATR", width=80),
            "ADX": st.column_config.NumberColumn("ADX", width=80),
            "Stochastic": st.column_config.NumberColumn("Stochastic", width=100),
            "Williams %R": st.column_config.NumberColumn("Williams %R", width=100),
            "CCI": st.column_config.NumberColumn("CCI", width=80),
            "Volume": st.column_config.TextColumn("Volume", width=120),
            "Market Cap": st.column_config.TextColumn("Market Cap", width=100)
        }
    )
    
    st.success("✅ Horizontal scrolling demonstration complete!")
    
    # Show table info
    st.subheader("📋 Table Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Columns", len(demo_df.columns))
    
    with col2:
        st.metric("Table Width", "1400px")
    
    with col3:
        st.metric("Rows", len(demo_df))
    
    st.markdown("""
    ### 🎯 **How to Test Horizontal Scrolling:**
    1. **Look for horizontal scrollbar** at the bottom of the table
    2. **Drag the scrollbar** or use arrow keys to scroll left/right
    3. **Mouse wheel + Shift** may also work for horizontal scrolling
    4. **All 18 columns** should be accessible through scrolling
    
    ### ✅ **Expected Behavior:**
    - Table width is fixed at 1400px
    - Horizontal scrollbar appears when table exceeds viewport width
    - All columns remain accessible through scrolling
    - Vertical scrolling also available with 400px height limit
    """)

if __name__ == "__main__":
    main()
