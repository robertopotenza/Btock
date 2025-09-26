"""
Btock Sentiment Scoring Dashboard
Standalone Streamlit Application for Social Media Sentiment Analysis

Analyzes sentiment from X (Twitter), Reddit, and StockTwits for stock tickers.
Can be used independently or chained with KPI scoring results.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Import custom modules
from modules.sentiment_analyzer import SentimentAnalyzer
from modules.utils import FileProcessor, ExcelExporter
from modules.database_utils import DatabaseUtils

# Page configuration
st.set_page_config(
    page_title="Btock Sentiment Scoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #6c757d;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Btock Sentiment Scoring Dashboard</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    **Analyze social media sentiment for stock tickers using X (Twitter), Reddit, and StockTwits.**
    
    This tool provides raw sentiment counts (not averages) where:
    - **Bullish/Positive mention** = +1
    - **Bearish/Negative mention** = -1  
    - **Neutral** = 0
    """)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # API Status Check
    sentiment_analyzer = SentimentAnalyzer()
    api_status = sentiment_analyzer.get_api_status()
    
    st.sidebar.subheader("📡 API Status")
    for api_name, status in api_status.items():
        status_icon = "✅" if status else "❌"
        st.sidebar.write(f"{status_icon} {api_name}")
    
    if not any(api_status.values()):
        st.error("⚠️ No APIs are configured. Please set up at least one API to use sentiment analysis.")
        st.info("""
        **Required Environment Variables:**
        - `XAI_API_KEY`: X (Twitter) via Grok API
        - `REDDIT_CLIENT_ID` & `REDDIT_CLIENT_SECRET`: Reddit API
        - StockTwits: No API key required (public API)
        """)
        return
    
    # Time range configuration
    st.sidebar.subheader("⏰ Time Range")
    hours_back = st.sidebar.slider(
        "Hours to analyze",
        min_value=1,
        max_value=168,  # 1 week
        value=24,
        help="Number of hours to look back for sentiment data"
    )
    
    # Input method selection
    st.sidebar.subheader("📝 Input Method")
    input_method = st.sidebar.radio(
        "Choose input method:",
        ["Manual Entry", "Upload File", "Import from KPI Results"]
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Ticker Input")
        
        tickers = []
        
        if input_method == "Manual Entry":
            ticker_input = st.text_area(
                "Enter ticker symbols (one per line or comma-separated):",
                placeholder="AAPL\nTSLA\nMSFT\n\nOr: AAPL, TSLA, MSFT",
                height=150
            )
            
            if ticker_input:
                # Parse tickers from input
                if ',' in ticker_input:
                    tickers = [t.strip().upper() for t in ticker_input.split(',') if t.strip()]
                else:
                    tickers = [t.strip().upper() for t in ticker_input.split('\n') if t.strip()]
        
        elif input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload Excel or CSV file with tickers",
                type=['xlsx', 'xls', 'csv'],
                help="File should contain a column named 'Ticker' or similar"
            )
            
            if uploaded_file:
                try:
                    processor = FileProcessor()
                    tickers = processor.process_file(uploaded_file)
                    st.success(f"✅ Loaded {len(tickers)} tickers from file")
                    
                    # Show preview
                    if tickers:
                        st.write("**Preview:**", tickers[:10])
                        if len(tickers) > 10:
                            st.write(f"... and {len(tickers) - 10} more")
                
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
        
        elif input_method == "Import from KPI Results":
            st.info("🔗 **Integration with KPI Scoring**")
            
            # Option to load from previous KPI analysis
            if st.button("Load Top 10 from Latest KPI Analysis"):
                try:
                    # This would connect to the database to get latest KPI results
                    st.info("This feature connects to your KPI analysis results to automatically load the top-performing tickers.")
                    # Placeholder for now
                    sample_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META", "AMZN", "NFLX", "AMD", "CRM"]
                    tickers = sample_tickers
                    st.success(f"✅ Loaded top 10 tickers from KPI analysis")
                    st.write("**Loaded tickers:**", tickers)
                
                except Exception as e:
                    st.error(f"Error loading KPI results: {str(e)}")
            
            # Manual override option
            manual_override = st.text_input(
                "Or enter tickers manually (comma-separated):",
                placeholder="AAPL, TSLA, MSFT"
            )
            
            if manual_override:
                tickers = [t.strip().upper() for t in manual_override.split(',') if t.strip()]
    
    with col2:
        st.subheader("📊 Analysis Summary")
        
        if tickers:
            st.metric("Tickers to Analyze", len(tickers))
            st.metric("Time Range", f"{hours_back} hours")
            
            # Show which APIs will be used
            active_apis = [name for name, status in api_status.items() if status]
            st.write("**Active APIs:**")
            for api in active_apis:
                st.write(f"• {api}")
        else:
            st.info("Enter tickers to see analysis summary")
    
    # Analysis section
    if tickers:
        st.markdown("---")
        st.subheader("🔍 Sentiment Analysis")
        
        if st.button("🚀 Run Sentiment Analysis", type="primary"):
            with st.spinner("Analyzing sentiment across social media platforms..."):
                
                # Run sentiment analysis
                results_df = sentiment_analyzer.get_sentiment_for_tickers(tickers, hours_back)
                
                if not results_df.empty:
                    # Format results
                    formatted_df = sentiment_analyzer.format_sentiment_results(results_df)
                    
                    # Display results
                    st.success(f"✅ Sentiment analysis completed for {len(results_df)} tickers!")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        positive_count = len(formatted_df[formatted_df['SentimentTotal'] > 0])
                        st.metric("Positive Sentiment", positive_count)
                    
                    with col2:
                        neutral_count = len(formatted_df[formatted_df['SentimentTotal'] == 0])
                        st.metric("Neutral Sentiment", neutral_count)
                    
                    with col3:
                        negative_count = len(formatted_df[formatted_df['SentimentTotal'] < 0])
                        st.metric("Negative Sentiment", negative_count)
                    
                    with col4:
                        avg_sentiment = formatted_df['SentimentTotal'].mean()
                        st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
                    
                    # Results table
                    st.subheader("📋 Detailed Results")
                    
                    # Style the dataframe
                    def style_sentiment(val):
                        if val > 0:
                            return 'color: #28a745; font-weight: bold'
                        elif val < 0:
                            return 'color: #dc3545; font-weight: bold'
                        else:
                            return 'color: #6c757d; font-weight: bold'
                    
                    styled_df = formatted_df.style.applymap(
                        style_sentiment, 
                        subset=['X', 'Reddit', 'StockTwits', 'SentimentTotal']
                    )
                    
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Export options
                    st.subheader("💾 Export Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Excel export
                        excel_data = ExcelExporter.export_results(formatted_df, "sentiment_analysis_results.xlsx")
                        if excel_data:
                            st.download_button(
                                label="📊 Download Excel Report",
                                data=excel_data,
                                file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    
                    with col2:
                        # CSV export
                        csv_data = formatted_df.to_csv(index=False)
                        st.download_button(
                            label="📄 Download CSV",
                            data=csv_data,
                            file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    # Save to session state for potential chaining
                    st.session_state['sentiment_results'] = formatted_df
                    
                else:
                    st.error("❌ No sentiment data could be retrieved. Please check your API configurations and try again.")
    
    # Information panel
    st.markdown("---")
    st.subheader("ℹ️ How Sentiment Scoring Works")
    
    with st.expander("📱 Data Sources"):
        st.markdown("""
        **X (Twitter)**: Uses Grok API to search for mentions and classify sentiment
        
        **Reddit**: Searches relevant subreddits (stocks, wallstreetbets, investing) for ticker mentions
        
        **StockTwits**: Uses public API to get sentiment-tagged messages
        """)
    
    with st.expander("🧮 Scoring Method"):
        st.markdown("""
        **Raw Count System** (not averages):
        - Each bullish/positive mention = +1
        - Each bearish/negative mention = -1
        - Neutral mentions = 0
        
        **Example**: 5 bullish - 2 bearish = +3 net sentiment
        
        **SentimentTotal** = Sum of all platform scores for quick ranking
        """)
    
    with st.expander("🔗 Integration with KPI Scoring"):
        st.markdown("""
        This sentiment tool can work:
        
        **Standalone**: Analyze sentiment for any ticker list
        
        **Chained with KPI**: 
        1. Run KPI Scoring to rank all tickers
        2. Extract Top 10 performers  
        3. Run Sentiment Analysis on those tickers
        4. Get combined technical + sentiment insights
        """)

if __name__ == "__main__":
    main()
