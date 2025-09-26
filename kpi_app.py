"""
Btock KPI Scoring Dashboard (Renamed from app.py)
Main Streamlit Application for Technical Indicator Analysis

This is the original KPI scoring application, now with optional sentiment analysis integration.
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
    page_title="Btock KPI Scoring Dashboard",
    page_icon="📈",
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
</style>
""", unsafe_allow_html=True)

def save_to_database(session_id: str, results: List[Dict], weights: Dict):
    """Save analysis results to database"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return
        
        conn = psycopg2.connect(database_url)
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
        conn.close()
        
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">📈 Btock KPI Scoring Dashboard</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    **Evaluate stocks daily using multiple technical indicators with weighted scoring system.**
    
    Upload tickers, configure weights, and get BUY/HOLD/SELL signals based on comprehensive technical analysis.
    """)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # File upload
    st.sidebar.subheader("📁 Upload Tickers")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel or CSV file",
        type=['xlsx', 'xls', 'csv'],
        help="File should contain a column with ticker symbols"
    )
    
    # Manual ticker entry
    manual_tickers = st.sidebar.text_area(
        "Or enter tickers manually:",
        placeholder="AAPL\nTSLA\nMSFT",
        help="One ticker per line"
    )
    
    # Process tickers
    tickers = []
    
    if uploaded_file:
        try:
            processor = FileProcessor()
            tickers = processor.process_file(uploaded_file)
            st.sidebar.success(f"✅ Loaded {len(tickers)} tickers")
        except Exception as e:
            st.sidebar.error(f"Error processing file: {str(e)}")
    
    elif manual_tickers:
        tickers = [t.strip().upper() for t in manual_tickers.split('\n') if t.strip()]
        st.sidebar.success(f"✅ {len(tickers)} tickers entered")
    
    # Weight configuration
    if tickers:
        st.sidebar.subheader("⚖️ Category Weights")
        
        weights = {}
        weights['momentum'] = st.sidebar.slider("Momentum", 0.0, 1.0, 0.25, 0.05)
        weights['trend'] = st.sidebar.slider("Trend", 0.0, 1.0, 0.25, 0.05)
        weights['volatility'] = st.sidebar.slider("Volatility", 0.0, 1.0, 0.20, 0.05)
        weights['strength'] = st.sidebar.slider("Strength", 0.0, 1.0, 0.15, 0.05)
        weights['support_resistance'] = st.sidebar.slider("Support/Resistance", 0.0, 1.0, 0.15, 0.05)
        
        # Normalize weights
        validator = WeightValidator()
        weights = validator.normalize_weights(weights)
        
        # Show normalized weights
        st.sidebar.write("**Normalized Weights:**")
        for category, weight in weights.items():
            st.sidebar.write(f"• {category.replace('_', ' ').title()}: {weight:.2f}")
        
        # Signal thresholds
        st.sidebar.subheader("🎯 Signal Thresholds")
        buy_threshold = st.sidebar.slider("BUY Threshold", 0.0, 1.0, 0.5, 0.1)
        sell_threshold = st.sidebar.slider("SELL Threshold", -1.0, 0.0, -0.5, 0.1)
    
    # Main content
    if tickers:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.subheader("📊 Analysis Summary")
            st.metric("Total Tickers", len(tickers))
            
            if len(tickers) <= 10:
                st.write("**Tickers:**")
                for ticker in tickers:
                    st.write(f"• {ticker}")
            else:
                st.write(f"**Sample:** {', '.join(tickers[:5])}...")
        
        with col1:
            st.subheader("🚀 Run Analysis")
            
            if st.button("Analyze Tickers", type="primary"):
                
                # Initialize components
                data_fetcher = DataFetcher()
                indicators = TechnicalIndicators()
                scoring_engine = ScoringEngine()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                
                for i, ticker in enumerate(tickers):
                    status_text.text(f"Analyzing {ticker}... ({i+1}/{len(tickers)})")
                    
                    try:
                        # Fetch data
                        data = data_fetcher.fetch_stock_data(ticker)
                        
                        if data is not None and not data.empty:
                            # Calculate indicators
                            indicator_values = indicators.calculate_all_indicators(data)
                            
                            # Calculate scores
                            scores = scoring_engine.calculate_category_scores(indicator_values)
                            final_score = scoring_engine.calculate_weighted_score(scores, weights)
                            
                            # Determine signal
                            if final_score >= buy_threshold:
                                signal = "BUY"
                            elif final_score <= sell_threshold:
                                signal = "SELL"
                            else:
                                signal = "HOLD"
                            
                            # Get current price
                            current_price = data['Close'].iloc[-1]
                            
                            result = {
                                'ticker': ticker,
                                'current_price': current_price,
                                'momentum_score': scores.get('momentum', 0),
                                'trend_score': scores.get('trend', 0),
                                'volatility_score': scores.get('volatility', 0),
                                'strength_score': scores.get('strength', 0),
                                'support_resistance_score': scores.get('support_resistance', 0),
                                'final_weighted_score': final_score,
                                'signal': signal
                            }
                            
                        else:
                            result = {
                                'ticker': ticker,
                                'error_message': 'No data available'
                            }
                    
                    except Exception as e:
                        result = {
                            'ticker': ticker,
                            'error_message': str(e)
                        }
                    
                    results.append(result)
                    progress_bar.progress((i + 1) / len(tickers))
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                if results:
                    st.success(f"✅ Analysis completed for {len(results)} tickers!")
                    
                    # Format results for display
                    formatter = DataFormatter()
                    results_df = formatter.format_results_table(results)
                    
                    if not results_df.empty:
                        # Summary statistics
                        summary_stats = formatter.create_summary_stats(results)
                        
                        if summary_stats:
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Successful Analysis", summary_stats.get('successful', 0))
                            with col2:
                                buy_count = summary_stats.get('signal_distribution', {}).get('BUY', 0)
                                st.metric("BUY Signals", buy_count)
                            with col3:
                                hold_count = summary_stats.get('signal_distribution', {}).get('HOLD', 0)
                                st.metric("HOLD Signals", hold_count)
                            with col4:
                                sell_count = summary_stats.get('signal_distribution', {}).get('SELL', 0)
                                st.metric("SELL Signals", sell_count)
                        
                        # Results table
                        st.subheader("📋 Analysis Results")
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Save results to session state for potential sentiment analysis
                        st.session_state['kpi_results'] = results_df
                        st.session_state['kpi_analysis_time'] = datetime.now()
                        
                        # Integration with Sentiment Analysis
                        st.markdown("---")
                        st.subheader("🔗 Next Step: Sentiment Analysis")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.info("""
                            **Want to add sentiment analysis to your top performers?**
                            
                            The sentiment scoring tool can analyze social media sentiment 
                            (X/Twitter, Reddit, StockTwits) for your highest-scoring tickers.
                            """)
                            
                            # Get top 10 tickers for sentiment analysis
                            top_tickers = results_df.head(10)['Ticker'].tolist() if not results_df.empty else []
                            
                            if top_tickers:
                                st.write(f"**Top 10 tickers for sentiment analysis:**")
                                st.write(", ".join(top_tickers))
                                
                                # Button to launch sentiment analysis
                                if st.button("🚀 Analyze Sentiment for Top 10", type="secondary"):
                                    st.session_state['sentiment_tickers'] = top_tickers
                                    st.success("✅ Top 10 tickers prepared for sentiment analysis!")
                                    st.info("💡 **Next:** Open the Sentiment Scoring Dashboard to continue analysis.")
                        
                        with col2:
                            st.markdown("""
                            **Integration Options:**
                            
                            1. **Manual**: Copy top tickers to sentiment tool
                            2. **Automatic**: Use the button to prepare tickers
                            3. **Standalone**: Run sentiment analysis independently
                            """)
                        
                        # Export options
                        st.subheader("💾 Export Results")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Excel export
                            from modules.utils import ExcelExporter
                            excel_data = ExcelExporter.export_results(results_df)
                            if excel_data:
                                st.download_button(
                                    label="📊 Download Excel Report",
                                    data=excel_data,
                                    file_name=f"kpi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        
                        with col2:
                            # CSV export
                            csv_data = results_df.to_csv(index=False)
                            st.download_button(
                                label="📄 Download CSV",
                                data=csv_data,
                                file_name=f"kpi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                        # Save to database
                        session_id = SessionManager.generate_session_id()
                        save_to_database(session_id, results, weights)
                    
                    else:
                        st.error("❌ No valid results to display")
                
                else:
                    st.error("❌ Analysis failed. Please check your tickers and try again.")
    
    else:
        st.info("👆 Upload a file or enter tickers manually to begin analysis")
    
    # Information panel
    st.markdown("---")
    st.subheader("ℹ️ How KPI Scoring Works")
    
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
    
    with st.expander("🔗 Integration with Sentiment Analysis"):
        st.markdown("""
        **Two-Step Workflow:**
        
        1. **KPI Scoring**: Rank all tickers by technical indicators
        2. **Sentiment Analysis**: Analyze social media sentiment for top performers
        
        **Benefits:**
        - Technical analysis identifies fundamentally strong stocks
        - Sentiment analysis adds market psychology insights
        - Combined approach provides comprehensive stock evaluation
        """)

if __name__ == "__main__":
    main()
