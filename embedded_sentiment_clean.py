"""
Clean Embedded Sentiment Analysis for Main KPI Dashboard
Provides clear single-mode operation (either demo or real API data, no mixing)
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def show_embedded_sentiment_analysis():
    """Show embedded sentiment analysis with clear single-mode operation"""
    
    st.markdown("---")
    st.subheader("📊 Sentiment Analysis (Optional)")
    
    try:
        # Check if we have KPI results
        if 'analysis_results' in st.session_state and st.session_state.analysis_results:
            results_df = pd.DataFrame(st.session_state.analysis_results)
            
            # Get top tickers with safe column checking
            if not results_df.empty and 'final_weighted_score' in results_df.columns and 'ticker' in results_df.columns:
                
                # Safely filter out error results
                valid_results = results_df.copy()
                
                # Only filter by error_message if the column exists
                if 'error_message' in results_df.columns:
                    try:
                        valid_results = results_df[
                            (results_df['error_message'].isna()) | 
                            (results_df['error_message'] == '') |
                            (results_df['error_message'].isnull())
                        ]
                    except Exception:
                        valid_results = results_df
                
                if not valid_results.empty and 'ticker' in valid_results.columns:
                    try:
                        # Get top tickers safely
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
                                default=top_tickers[:5] if len(top_tickers) >= 5 else top_tickers,
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
                            
                            try:
                                # Import sentiment analyzer
                                from modules.sentiment_analyzer import SentimentAnalyzer
                                
                                # Initialize sentiment analyzer
                                analyzer = SentimentAnalyzer()
                                
                                # Show mode information
                                if analyzer.demo_mode:
                                    st.info("""
                                    🎯 **Demo Mode Active**
                                    
                                    Using simulated sentiment data for demonstration. 
                                    Configure API keys (XAI_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET) for real social media data.
                                    """)
                                else:
                                    st.success("🚀 **Live Mode Active** - Using real social media data from configured APIs.")
                                
                                # Run sentiment analysis
                                with st.spinner(f"Analyzing sentiment for {len(selected_tickers)} tickers..."):
                                    sentiment_results = analyzer.get_sentiment_for_tickers(selected_tickers, hours_back)
                                
                                if not sentiment_results.empty:
                                    # Format and display results
                                    formatted_results = analyzer.format_sentiment_results(sentiment_results)
                                    
                                    mode_text = "Demo" if analyzer.demo_mode else "Live"
                                    st.success(f"✅ {mode_text} sentiment analysis completed for {len(formatted_results)} tickers!")
                                    
                                    # Display results
                                    st.subheader("📊 Sentiment Analysis Results")
                                    
                                    # Summary metrics
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        positive_count = len(formatted_results[formatted_results['SentimentTotal'] > 1])
                                        st.metric("Positive Sentiment", positive_count)
                                    
                                    with col2:
                                        neutral_count = len(formatted_results[formatted_results['SentimentTotal'].between(-1, 1)])
                                        st.metric("Neutral Sentiment", neutral_count)
                                    
                                    with col3:
                                        negative_count = len(formatted_results[formatted_results['SentimentTotal'] < -1])
                                        st.metric("Negative Sentiment", negative_count)
                                    
                                    with col4:
                                        avg_sentiment = formatted_results['SentimentTotal'].mean()
                                        st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
                                    
                                    # Results table
                                    st.dataframe(formatted_results, width='stretch')
                                    
                                    # Export options
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # CSV export
                                        csv_data = formatted_results.to_csv(index=False)
                                        filename_suffix = "demo" if analyzer.demo_mode else "live"
                                        st.download_button(
                                            label=f"📄 Download {mode_text} Sentiment CSV",
                                            data=csv_data,
                                            file_name=f"sentiment_analysis_{filename_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                            mime="text/csv"
                                        )
                                    
                                    with col2:
                                        # Combined analysis export
                                        try:
                                            if not valid_results.empty and all(col in valid_results.columns for col in ['ticker', 'final_weighted_score']):
                                                kpi_columns = ['ticker', 'final_weighted_score']
                                                if 'signal' in valid_results.columns:
                                                    kpi_columns.append('signal')
                                                
                                                kpi_top = valid_results.nlargest(10, 'final_weighted_score')[kpi_columns]
                                                combined = pd.merge(kpi_top, formatted_results, left_on='ticker', right_on='Ticker', how='left')
                                                
                                                combined_csv = combined.to_csv(index=False)
                                                st.download_button(
                                                    label=f"📊 Download Combined KPI+{mode_text} Analysis",
                                                    data=combined_csv,
                                                    file_name=f"combined_kpi_sentiment_{filename_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                                    mime="text/csv"
                                                )
                                        except Exception as e:
                                            st.warning(f"Could not create combined export: {e}")
                                    
                                    # Store sentiment results
                                    st.session_state['sentiment_results'] = formatted_results
                                    
                                else:
                                    st.error("❌ No sentiment data could be retrieved.")
                            
                            except ImportError as e:
                                st.error(f"❌ Could not import sentiment analyzer: {e}")
                            except Exception as e:
                                st.error(f"❌ Error during sentiment analysis: {e}")
                        
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
                                try:
                                    from modules.sentiment_analyzer import SentimentAnalyzer
                                    analyzer = SentimentAnalyzer()
                                    
                                    with st.spinner(f"Analyzing sentiment for {len(custom_tickers)} custom tickers..."):
                                        custom_results = analyzer.get_sentiment_for_tickers(custom_tickers, hours_back)
                                    
                                    if not custom_results.empty:
                                        formatted_custom = analyzer.format_sentiment_results(custom_results)
                                        st.dataframe(formatted_custom, width='stretch')
                                except Exception as e:
                                    st.error(f"❌ Error analyzing custom tickers: {e}")
                    
                    except Exception as e:
                        st.error(f"❌ Error processing KPI results: {e}")
                
                else:
                    st.info("No valid KPI results available for sentiment analysis. Run KPI analysis first.")
            
            else:
                st.info("KPI analysis results missing required columns. Run KPI analysis first.")
        
        else:
            st.info("""
            **Sentiment Analysis Available**
            
            After running KPI analysis above, you'll be able to:
            - Automatically analyze sentiment for your top-performing tickers
            - Get social media insights from X (Twitter), Reddit, and StockTwits
            - Export combined KPI + sentiment results
            
            **Two Modes Available:**
            - **Demo Mode**: Simulated data for testing (no API keys needed)
            - **Live Mode**: Real social media data (requires API configuration)
            """)
    
    except Exception as e:
        st.error(f"❌ Error in sentiment analysis section: {e}")
        st.info("The sentiment analysis feature encountered an error. You can still use the standalone sentiment tool by running: `streamlit run sentiment_app.py`")
