#!/usr/bin/env python3
"""
Final Enhancements Test Script
Tests horizontal scrolling and sentiment dropdown functionality
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_table_scrolling():
    """Test horizontal scrolling functionality"""
    st.header("🧪 Testing Table Horizontal Scrolling")
    
    # Create a wide test dataframe
    test_data = {
        'Ticker': ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN'],
        'Price': [175.43, 242.65, 338.11, 138.21, 144.05],
        'Final Score': [0.6543, 0.4321, 0.7890, 0.3456, 0.5678],
        'Signal': ['BUY', 'HOLD', 'BUY', 'HOLD', 'BUY'],
        'Momentum Score': [0.45, 0.23, 0.67, 0.12, 0.34],
        'Trend Score': [0.78, 0.56, 0.89, 0.45, 0.67],
        'Volatility Score': [0.34, 0.67, 0.23, 0.78, 0.45],
        'Strength Score': [0.56, 0.34, 0.78, 0.23, 0.56],
        'Support/Resistance': [0.67, 0.45, 0.34, 0.67, 0.78],
        'RSI': [65.4, 45.2, 72.1, 38.9, 58.7],
        'MACD': [0.45, -0.23, 0.67, -0.12, 0.34],
        'ATR': [2.34, 8.67, 3.45, 4.23, 5.67],
        'ADX': [25.6, 18.9, 32.4, 15.7, 28.3],
        'Stochastic': [78.9, 34.5, 85.2, 23.1, 67.4],
        'Williams %R': [-15.6, -67.8, -12.3, -78.9, -34.5],
        'CCI': [145.6, -89.3, 167.8, -123.4, 78.9]
    }
    
    test_df = pd.DataFrame(test_data)
    
    st.info("This table should have horizontal scrolling enabled. Try scrolling horizontally to see all columns.")
    
    # Test the exact same configuration as in app.py
    st.dataframe(
        test_df,
        width='stretch',
        height=400,                    # Fixed height for scrolling
        hide_index=True,
        use_container_width=False,     # Enables horizontal scrolling
        column_config={
            "Signal": st.column_config.TextColumn(
                "Signal",
                help="BUY/HOLD/SELL recommendation"
            ),
            "Final Score": st.column_config.NumberColumn(
                "Final Score",
                help="Weighted score (-1 to +1)",
                format="%.4f"
            )
        }
    )
    
    st.success("✅ Table scrolling test completed!")
    return True

def test_sentiment_dropdown():
    """Test sentiment analysis dropdown functionality"""
    st.header("🧪 Testing Sentiment Dropdown Selection")
    
    # Create mock top tickers
    mock_tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 'CRM', 'AMD', 
                   'INTC', 'ORCL', 'CSCO', 'ADBE', 'PYPL', 'UBER', 'SPOT', 'ZOOM', 'DOCU', 'TWTR']
    
    st.info("Testing the sentiment analysis ticker selection with dropdown functionality.")
    
    # Replicate the exact layout from embedded_sentiment_production.py
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Initialize session state for selected tickers if not exists
        if 'test_sentiment_selected_tickers' not in st.session_state:
            st.session_state.test_sentiment_selected_tickers = mock_tickers[:5]
        
        # Allow user to modify the ticker list
        selected_tickers = st.multiselect(
            "Select tickers for sentiment analysis:",
            options=mock_tickers,
            default=st.session_state.test_sentiment_selected_tickers,
            help="Choose which tickers to analyze for social media sentiment",
            key="test_multiselect"
        )
    
    with col2:
        # Top N selection
        top_n_option = st.selectbox(
            "Quick select:",
            options=[5, 10, 20],
            index=0,
            help="Quickly select top N performers",
            key="test_selectbox"
        )
        
        # Button to apply top N selection
        if st.button("Select Top " + str(top_n_option), key="test_select_top_n"):
            # Update the multiselect with top N tickers
            selected_top_tickers = mock_tickers[:top_n_option] if len(mock_tickers) >= top_n_option else mock_tickers
            st.session_state.test_sentiment_selected_tickers = selected_top_tickers
            st.rerun()
    
    with col3:
        # Time range selection
        hours_back = st.selectbox(
            "Analysis time range:",
            options=[6, 12, 24, 48, 72, 168],
            index=2,  # Default to 24 hours
            format_func=lambda x: f"{x} hours" if x < 168 else "1 week",
            key="test_hours"
        )
    
    # Display current selection
    st.write("**Current Selection:**")
    st.write(f"Selected tickers: {selected_tickers}")
    st.write(f"Quick select option: Top {top_n_option}")
    st.write(f"Time range: {hours_back} hours" if hours_back < 168 else "Time range: 1 week")
    
    # Test the selection functionality
    if st.button("🧪 Test Selection", key="test_selection"):
        st.success(f"✅ Successfully selected {len(selected_tickers)} tickers for analysis!")
        st.json({
            "selected_tickers": selected_tickers,
            "top_n_option": top_n_option,
            "hours_back": hours_back
        })
    
    return True

def test_session_state_persistence():
    """Test session state persistence for sentiment selection"""
    st.header("🧪 Testing Session State Persistence")
    
    st.info("This test verifies that ticker selections persist across interactions.")
    
    # Show current session state
    if 'test_sentiment_selected_tickers' in st.session_state:
        st.write("**Current session state:**")
        st.json(st.session_state.test_sentiment_selected_tickers)
        st.success("✅ Session state is working correctly!")
    else:
        st.warning("⚠️ Session state not initialized yet. Use the dropdown test above first.")
    
    return True

def main():
    """Main test function"""
    st.set_page_config(
        page_title="Btock - Final Enhancements Test",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Btock Final Enhancements Test Suite")
    st.markdown("Testing horizontal scrolling and sentiment dropdown functionality")
    
    # Test 1: Table Scrolling
    with st.expander("📊 Table Horizontal Scrolling Test", expanded=True):
        try:
            test_table_scrolling()
        except Exception as e:
            st.error(f"❌ Table scrolling test failed: {e}")
    
    # Test 2: Sentiment Dropdown
    with st.expander("🎯 Sentiment Dropdown Selection Test", expanded=True):
        try:
            test_sentiment_dropdown()
        except Exception as e:
            st.error(f"❌ Sentiment dropdown test failed: {e}")
    
    # Test 3: Session State
    with st.expander("💾 Session State Persistence Test", expanded=True):
        try:
            test_session_state_persistence()
        except Exception as e:
            st.error(f"❌ Session state test failed: {e}")
    
    # Summary
    st.markdown("---")
    st.subheader("📋 Test Summary")
    st.markdown("""
    **Expected Results:**
    1. ✅ **Table Scrolling**: Wide table should scroll horizontally with fixed height
    2. ✅ **Sentiment Dropdown**: Quick selection buttons should update multiselect
    3. ✅ **Session State**: Selections should persist across interactions
    
    **How to Test:**
    1. Scroll horizontally in the analysis results table
    2. Use "Select Top N" buttons to quickly select tickers
    3. Verify selections persist when you interact with other elements
    """)

if __name__ == "__main__":
    main()
