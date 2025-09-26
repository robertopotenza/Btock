"""
Embedded Sentiment Analysis for Main KPI Dashboard
This provides sentiment analysis functionality within the main app
"""

import streamlit as st
import pandas as pd
from modules.sentiment_analyzer import SentimentAnalyzer
from datetime import datetime

def show_embedded_sentiment_analysis():
    """Show embedded sentiment analysis in the main KPI dashboard"""
    
    st.markdown("---")
    st.subheader("📊 Sentiment Analysis (Optional)")
    
    # Check if we have KPI results
    if 'analysis_results' in st.session_state and st.session_state.analysis_results:
        results_df = pd.DataFrame(st.session_state.analysis_results)
        
        # Get top tickers
        if not results_df.empty and 'final_weighted_score' in results_df.columns:
            # Filter out error results (safely check if error_message column exists)
            if 'error_message' in results_df.columns:
                valid_results = results_df[results_df['error_message'].isna() | (results_df['error_message'] == '')]
            else:
                valid_results = results_df
            
            if not valid_results.empty and 'ticker' in valid_results.columns:
                top_tickers = valid_results.nlargest(10, 'final_weighted_score')['ticker'].tolist()
                
                st.info(f"""
                **Ready for Sentiment Analysis!**
                
                Top 10 performing tickers from your KPI analysis:
                {', '.join(top_tickers[:5])}{'...' if len(top_tickers) > 5 else ''}
                """)
                
                # Sentiment analysis controls
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Allow user to modify the ticker list
                    selected_tickers = st.multiselect(
                        "Select tickers for sentiment analysis:",
                        options=top_tickers,
                        default=top_tickers[:5],  # Default to top 5
                        help="Choose which tickers to analyze for sentiment"
                    )
                
                with col2:
                    # Time range selection
                    hours_back = st.selectbox(
                        "Analysis time range:",
                        options=[6, 12, 24, 48, 72, 168],
                        index=2,  # Default to 24 hours
                        format_func=lambda x: f"{x} hours" if x < 168 else "1 week"
                    )
                
                # Run sentiment analysis button
                if selected_tickers and st.button("🚀 Run Sentiment Analysis", type="primary"):
                    
                    # Initialize sentiment analyzer
                    analyzer = SentimentAnalyzer()
                    
                    # Check API status
                    api_status = analyzer.get_api_status()
                    active_apis = [name for name, status in api_status.items() if status]
                    
                    if not active_apis:
                        st.warning("""
                        ⚠️ **No APIs Configured**
                        
                        To use sentiment analysis, you need to configure at least one API:
                        - **X (Twitter)**: Set `XAI_API_KEY` environment variable
                        - **Reddit**: Set `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
                        - **StockTwits**: Available by default (no setup required)
                        """)
                    else:
                        st.info(f"Using APIs: {', '.join(active_apis)}")
                        
                        # Run sentiment analysis
                        with st.spinner(f"Analyzing sentiment for {len(selected_tickers)} tickers..."):
                            sentiment_results = analyzer.get_sentiment_for_tickers(selected_tickers, hours_back)
                        
                        if not sentiment_results.empty:
                            # Format and display results
                            formatted_results = analyzer.format_sentiment_results(sentiment_results)
                            
                            st.success(f"✅ Sentiment analysis completed for {len(formatted_results)} tickers!")
                            
                            # Display results
                            st.subheader("📊 Sentiment Analysis Results")
                            
                            # Summary metrics
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                positive_count = len(formatted_results[formatted_results['SentimentTotal'] > 0])
                                st.metric("Positive Sentiment", positive_count)
                            
                            with col2:
                                neutral_count = len(formatted_results[formatted_results['SentimentTotal'] == 0])
                                st.metric("Neutral Sentiment", neutral_count)
                            
                            with col3:
                                negative_count = len(formatted_results[formatted_results['SentimentTotal'] < 0])
                                st.metric("Negative Sentiment", negative_count)
                            
                            with col4:
                                avg_sentiment = formatted_results['SentimentTotal'].mean()
                                st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
                            
                            # Results table
                            st.dataframe(formatted_results, use_container_width=True)
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # CSV export
                                csv_data = formatted_results.to_csv(index=False)
                                st.download_button(
                                    label="📄 Download Sentiment CSV",
                                    data=csv_data,
                                    file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                            
                            with col2:
                            # Combined analysis export
                            if not valid_results.empty and all(col in valid_results.columns for col in ['ticker', 'final_weighted_score']):
                                # Merge KPI and sentiment results
                                kpi_columns = ['ticker', 'final_weighted_score']
                                if 'signal' in valid_results.columns:
                                    kpi_columns.append('signal')
                                
                                kpi_top = valid_results.nlargest(10, 'final_weighted_score')[kpi_columns]
                                combined = pd.merge(kpi_top, formatted_results, left_on='ticker', right_on='Ticker', how='left')
                                    
                                    combined_csv = combined.to_csv(index=False)
                                    st.download_button(
                                        label="📊 Download Combined Analysis",
                                        data=combined_csv,
                                        file_name=f"combined_kpi_sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            
                            # Store sentiment results
                            st.session_state['sentiment_results'] = formatted_results
                            
                        else:
                            st.error("❌ No sentiment data could be retrieved. Please check your API configurations.")
                
                # Alternative: Manual ticker entry for sentiment
                st.markdown("---")
                st.subheader("🔧 Custom Sentiment Analysis")
                
                manual_tickers = st.text_input(
                    "Or enter custom tickers for sentiment analysis (comma-separated):",
                    placeholder="AAPL, TSLA, MSFT",
                    help="Enter any tickers you want to analyze for sentiment"
                )
                
                if manual_tickers:
                    custom_tickers = [t.strip().upper() for t in manual_tickers.split(',') if t.strip()]
                    
                    if st.button("🔍 Analyze Custom Tickers", key="custom_sentiment"):
                        analyzer = SentimentAnalyzer()
                        
                        with st.spinner(f"Analyzing sentiment for {len(custom_tickers)} custom tickers..."):
                            custom_results = analyzer.get_sentiment_for_tickers(custom_tickers, hours_back)
                        
                        if not custom_results.empty:
                            formatted_custom = analyzer.format_sentiment_results(custom_results)
                            st.dataframe(formatted_custom, use_container_width=True)
            
            else:
                st.info("No valid KPI results available for sentiment analysis. Run KPI analysis first.")
        
        else:
            st.info("Run KPI analysis first to get tickers for sentiment analysis.")
    
    else:
        st.info("""
        **Sentiment Analysis Available**
        
        After running KPI analysis above, you'll be able to:
        - Automatically analyze sentiment for your top-performing tickers
        - Get social media insights from X (Twitter), Reddit, and StockTwits
        - Export combined KPI + sentiment results
        """)
        
        # Show standalone option
        st.markdown("**Or use the standalone sentiment tool:**")
        st.code("streamlit run sentiment_app.py", language="bash")
