"""
Btock Stock KPI Scoring Dashboard
Main Streamlit Application

A web-based dashboard for evaluating stocks daily using multiple KPIs
with a weighted scoring system and BUY/HOLD/SELL signals.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import psycopg2
from datetime import datetime
import json
from typing import Dict, List

# Import custom modules
from modules.data_fetcher import DataFetcher
from modules.indicators import TechnicalIndicators
from modules.scoring import ScoringEngine
from modules.utils import FileProcessor, WeightValidator, SessionManager, DataFormatter
from modules.database_utils import DatabaseUtils

# Page configuration
st.set_page_config(
    page_title="Btock - Stock KPI Scoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .sell-signal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .hold-signal {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = SessionManager.generate_session_id()
if 'weights' not in st.session_state:
    st.session_state.weights = WeightValidator.get_default_weights()

# Database connection
@st.cache_resource
def init_database():
    """Initialize database connection"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url)
            return conn
        else:
            st.warning("Database connection not configured. Results will not be persisted.")
            return None
    except Exception as e:
        st.warning(f"Database connection failed: {str(e)}")
        return None

def save_to_database(conn, session_id: str, results: List[Dict], weights: Dict[str, float]):
    """Save analysis results to database"""
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Save session info
        cursor.execute("""
            INSERT INTO analysis_sessions (session_id, weights, total_tickers, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (session_id) DO UPDATE SET
            weights = EXCLUDED.weights,
            total_tickers = EXCLUDED.total_tickers,
            status = EXCLUDED.status
        """, (session_id, json.dumps(weights), len(results), 'completed'))
        
        # Save ticker results
        for result in results:
            # Prepare result for database insertion
            prepared_result = DatabaseUtils.prepare_result_for_database(result)
            
            DatabaseUtils.safe_database_insert(cursor, """
                INSERT INTO ticker_results (
                    session_id, ticker, current_price, momentum_score, trend_score,
                    volatility_score, strength_score, support_resistance_score,
                    final_weighted_score, signal, error_message
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id,
                prepared_result.get('ticker', ''),
                prepared_result.get('current_price'),
                prepared_result.get('momentum_score'),
                prepared_result.get('trend_score'),
                prepared_result.get('volatility_score'),
                prepared_result.get('strength_score'),
                prepared_result.get('support_resistance_score'),
                prepared_result.get('final_weighted_score'),
                prepared_result.get('signal'),
                prepared_result.get('error_message')
            ))
        
        conn.commit()
        cursor.close()
        
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        conn.rollback()

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Btock Stock KPI Scoring Dashboard</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    **Evaluate stocks daily using multiple technical indicators with a weighted scoring system.**
    
    Upload a list of tickers, configure weights for different analysis categories, and get BUY/HOLD/SELL signals 
    with detailed scoring across Momentum, Trend, Volatility, Strength, and Support/Resistance categories.
    """)
    
    # Initialize components
    data_fetcher = DataFetcher()
    indicators_calculator = TechnicalIndicators()
    scoring_engine = ScoringEngine()
    
    # Initialize database
    db_conn = init_database()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File upload section
        st.subheader("📁 Upload Ticker List")
        uploaded_file = st.file_uploader(
            "Upload Excel or CSV file with ticker symbols",
            type=['csv', 'xlsx', 'xls'],
            help="File must contain a column named 'Ticker' with stock symbols"
        )
        
        # Manual ticker input
        st.subheader("✏️ Manual Input")
        manual_tickers = st.text_area(
            "Enter tickers (one per line or comma-separated)",
            placeholder="AAPL\nMSFT\nGOOGL\nTSLA",
            help="Enter stock ticker symbols manually"
        )
        
        # Weight configuration
        st.subheader("⚖️ Category Weights")
        st.markdown("Configure the importance of each analysis category:")
        
        momentum_weight = st.slider("Momentum", 0.0, 1.0, st.session_state.weights['momentum'], 0.05)
        trend_weight = st.slider("Trend", 0.0, 1.0, st.session_state.weights['trend'], 0.05)
        volatility_weight = st.slider("Volatility", 0.0, 1.0, st.session_state.weights['volatility'], 0.05)
        strength_weight = st.slider("Strength", 0.0, 1.0, st.session_state.weights['strength'], 0.05)
        support_resistance_weight = st.slider("Support/Resistance", 0.0, 1.0, st.session_state.weights['support_resistance'], 0.05)
        
        # Update weights
        new_weights = {
            'momentum': momentum_weight,
            'trend': trend_weight,
            'volatility': volatility_weight,
            'strength': strength_weight,
            'support_resistance': support_resistance_weight
        }
        
        # Validate and normalize weights
        normalized_weights, weights_valid = WeightValidator.validate_and_normalize_weights(new_weights)
        if weights_valid:
            st.session_state.weights = normalized_weights
        
        # Display normalized weights
        st.markdown("**Normalized Weights:**")
        for category, weight in st.session_state.weights.items():
            st.text(f"{category.replace('_', ' ').title()}: {weight:.3f}")
        
        # Signal thresholds
        st.subheader("🎯 Signal Thresholds")
        buy_threshold = st.slider("BUY Threshold", -1.0, 1.0, 0.5, 0.1)
        sell_threshold = st.slider("SELL Threshold", -1.0, 1.0, -0.5, 0.1)
        
        scoring_engine.set_thresholds(buy_threshold, sell_threshold)
        
        # Reset button
        if st.button("🔄 Reset to Defaults"):
            st.session_state.weights = WeightValidator.get_default_weights()
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Process ticker input
        tickers = []
        
        if uploaded_file:
            tickers = FileProcessor.process_uploaded_file(uploaded_file)
        elif manual_tickers:
            # Process manual input
            manual_list = []
            if ',' in manual_tickers:
                manual_list = [t.strip() for t in manual_tickers.split(',')]
            else:
                manual_list = [t.strip() for t in manual_tickers.split('\n')]
            
            # Clean tickers
            for ticker in manual_list:
                cleaned = FileProcessor.clean_ticker_symbol(ticker)
                if cleaned:
                    tickers.append(cleaned)
            
            if tickers:
                st.success(f"Loaded {len(tickers)} ticker symbols from manual input.")
        
        # Analysis section
        if tickers:
            st.subheader(f"📈 Analysis for {len(tickers)} Tickers")
            
            # Limit check
            if len(tickers) > 250:
                st.warning(f"You have {len(tickers)} tickers. Analysis may take a while. Consider reducing the list for faster results.")
            
            # Analysis button
            if st.button("🚀 Run Analysis", type="primary"):
                
                # Progress tracking
                progress_container = st.container()
                
                with progress_container:
                    st.info("Starting analysis...")
                    
                    # Validate tickers first
                    with st.spinner("Validating tickers..."):
                        valid_tickers, invalid_tickers = data_fetcher.validate_tickers_batch(tickers)
                    
                    if invalid_tickers:
                        st.warning(f"Invalid tickers found: {', '.join(invalid_tickers)}")
                    
                    if not valid_tickers:
                        st.error("No valid tickers found. Please check your input.")
                        return
                    
                    st.success(f"Proceeding with {len(valid_tickers)} valid tickers.")
                    
                    # Fetch data and analyze
                    results = []
                    
                    # Create progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, ticker in enumerate(valid_tickers):
                        # Update progress
                        progress = (i + 1) / len(valid_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Analyzing {ticker} ({i + 1}/{len(valid_tickers)})")
                        
                        try:
                            # Fetch stock data
                            stock_data = data_fetcher.fetch_stock_data(ticker)
                            
                            if stock_data is None or stock_data.empty:
                                results.append({
                                    'ticker': ticker,
                                    'error_message': 'No data available'
                                })
                                continue
                            
                            # Get current price
                            current_price = data_fetcher.get_current_price(ticker)
                            
                            # Calculate indicators
                            indicators = indicators_calculator.calculate_all_indicators(stock_data)
                            
                            if not indicators:
                                results.append({
                                    'ticker': ticker,
                                    'current_price': current_price,
                                    'error_message': 'Insufficient data for analysis'
                                })
                                continue
                            
                            # Analyze ticker
                            analysis_result = scoring_engine.analyze_ticker(indicators, st.session_state.weights)
                            
                            # Combine results
                            result = {
                                'ticker': ticker,
                                'current_price': current_price,
                                **analysis_result
                            }
                            
                            results.append(result)
                            
                        except Exception as e:
                            results.append({
                                'ticker': ticker,
                                'error_message': f'Analysis error: {str(e)}'
                            })
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Store results
                    st.session_state.analysis_results = results
                    
                    # Save to database
                    if db_conn:
                        save_to_database(db_conn, st.session_state.session_id, results, st.session_state.weights)
                    
                    st.success(f"Analysis completed for {len(results)} tickers!")
        
        # Display results
        if st.session_state.analysis_results:
            st.subheader("📊 Analysis Results")
            
            # Format results for display
            display_df = DataFormatter.format_results_for_display(st.session_state.analysis_results)
            
            if not display_df.empty:
                # Display interactive table
                st.dataframe(
                    display_df,
                    width='stretch',
                    hide_index=True,
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
                
                # Download button
                excel_data = FileProcessor.create_results_excel(
                    pd.DataFrame(st.session_state.analysis_results)
                )
                
                if excel_data:
                    st.download_button(
                        label="📥 Download Results as Excel",
                        data=excel_data,
                        file_name=f"btock_analysis_{st.session_state.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    with col2:
        # Summary statistics
        if st.session_state.analysis_results:
            st.subheader("📈 Summary Statistics")
            
            summary = DataFormatter.create_summary_stats(st.session_state.analysis_results)
            
            if summary:
                # Basic stats
                st.metric("Total Analyzed", summary['total_analyzed'])
                st.metric("Successful", summary['successful'])
                st.metric("Errors", summary['errors'])
                
                # Signal distribution
                if 'signal_distribution' in summary:
                    st.markdown("**Signal Distribution:**")
                    signals = summary['signal_distribution']
                    
                    col_buy, col_hold, col_sell = st.columns(3)
                    with col_buy:
                        st.metric("BUY", signals['BUY'])
                    with col_hold:
                        st.metric("HOLD", signals['HOLD'])
                    with col_sell:
                        st.metric("SELL", signals['SELL'])
                
                # Score statistics
                if 'score_stats' in summary:
                    st.markdown("**Score Statistics:**")
                    stats = summary['score_stats']
                    st.metric("Average Score", f"{stats['mean']:.4f}")
                    st.metric("Score Range", f"{stats['min']:.4f} to {stats['max']:.4f}")
        
        # Information panel
        st.subheader("ℹ️ How It Works")
        
        with st.expander("📋 Analysis Categories"):
            st.markdown("""
            **Momentum**: RSI, Stochastic, Williams %R, ROC, Ultimate Oscillator
            
            **Trend**: MACD, Moving Averages, Bull/Bear Power
            
            **Volatility**: ATR, High/Low Analysis
            
            **Strength**: ADX, CCI, Directional Movement
            
            **Support/Resistance**: Pivot Points (Classic, Fibonacci, Camarilla, Woodie, DeMark)
            """)
        
        with st.expander("🎯 Scoring System"):
            st.markdown("""
            Each indicator is normalized to a -1 to +1 scale:
            - **+1**: Strong bullish signal
            - **0**: Neutral
            - **-1**: Strong bearish signal
            
            Category scores are averaged, then weighted according to your preferences.
            
            **Final Score** determines the signal:
            - **BUY**: Score ≥ 0.5
            - **HOLD**: -0.5 < Score < 0.5  
            - **SELL**: Score ≤ -0.5
            """)
        
        with st.expander("📊 Data Source"):
            st.markdown("""
            **Yahoo Finance** provides historical OHLCV data.
            
            Technical indicators calculated using **pandas_ta** library.
            
            Analysis covers the last 1 year of trading data for comprehensive indicator calculation.
            """)

    # Import and show embedded sentiment analysis (production version with troubleshooting)
    try:
        from embedded_sentiment_production import show_embedded_sentiment_analysis
        show_embedded_sentiment_analysis()
    except Exception as e:
        st.error(f"Error loading sentiment analysis: {e}")
        st.info("For troubleshooting help, check the SENTIMENT_TROUBLESHOOTING.md guide in the repository.")

if __name__ == "__main__":
    main()
