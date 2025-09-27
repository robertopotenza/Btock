"""
Production Embedded Sentiment Analysis for Main KPI Dashboard
Focuses on real API configuration and troubleshooting guidance
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def show_embedded_sentiment_analysis():
    """Show embedded sentiment analysis with production focus and troubleshooting"""
    
    st.markdown("---")
    st.subheader("📊 Sentiment Analysis")
    
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
                        **Ready for Social Media Sentiment Analysis!**
                        
                        Top 10 performing tickers from your KPI analysis:
                        {', '.join(top_tickers[:5])}{'...' if len(top_tickers) > 5 else ''}
                        
                        Get real-time sentiment from X (Twitter), Reddit, and StockTwits.
                        """)
                        
                        # Sentiment analysis controls
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            # Initialize session state for selected tickers if not exists
                            if 'sentiment_selected_tickers' not in st.session_state:
                                st.session_state.sentiment_selected_tickers = top_tickers[:5] if len(top_tickers) >= 5 else top_tickers
                            
                            # Allow user to modify the ticker list
                            selected_tickers = st.multiselect(
                                "Select tickers for sentiment analysis:",
                                options=top_tickers,
                                default=st.session_state.sentiment_selected_tickers,
                                help="Choose which tickers to analyze for social media sentiment"
                            )
                        
                        with col2:
                            # Top N selection
                            top_n_option = st.selectbox(
                                "Quick select:",
                                options=[5, 10, 20],
                                index=0,
                                help="Quickly select top N performers"
                            )
                            
                            # Button to apply top N selection
                            if st.button("Select Top " + str(top_n_option), key="select_top_n"):
                                # Update the multiselect with top N tickers
                                selected_top_tickers = top_tickers[:top_n_option] if len(top_tickers) >= top_n_option else top_tickers
                                st.session_state.sentiment_selected_tickers = selected_top_tickers
                                st.rerun()
                        
                        with col3:
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
                                
                                # Run sentiment analysis (will show setup guidance if APIs not configured)
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
                                        st.download_button(
                                            label="📄 Download Sentiment CSV",
                                            data=csv_data,
                                            file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
                                                    label="📊 Download Combined KPI+Sentiment Analysis",
                                                    data=combined_csv,
                                                    file_name=f"combined_kpi_sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                                    mime="text/csv"
                                                )
                                        except Exception as e:
                                            st.warning(f"Could not create combined export: {e}")
                                    
                                    # Store sentiment results
                                    st.session_state['sentiment_results'] = formatted_results
                                    
                                    # Show data sources used
                                    working_apis = [name for name, status in analyzer.api_status.items() if status]
                                    if working_apis:
                                        st.info(f"📡 **Data Sources Used**: {', '.join(working_apis)}")
                                
                                # If empty results, the analyzer already showed setup guidance
                            
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
                        
                        # Troubleshooting section
                        with st.expander("🔧 API Setup & Troubleshooting"):
                            st.markdown("""
                            ### **Quick Setup Guide**
                            
                            **1. X (Twitter) via Grok API**
                            - Get API key from: https://x.ai/
                            - Set environment variable: `XAI_API_KEY=your_key`
                            
                            **2. Reddit API**
                            - Create app at: https://www.reddit.com/prefs/apps
                            - Set variables: `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
                            
                            **3. StockTwits**
                            - No setup required (public API)
                            
                            ### **Common Issues**
                            - **404 Errors**: Check API key validity and endpoint URL
                            - **403 Errors**: Rate limiting or authentication issues  
                            - **No Results**: Verify environment variables are set in Railway
                            
                            ### **Testing APIs**
                            After setting environment variables, restart the application and try sentiment analysis again.
                            """)
                    
                    except Exception as e:
                        st.error(f"❌ Error processing KPI results: {e}")
                
                else:
                    st.info("No valid KPI results available for sentiment analysis. Run KPI analysis first.")
            
            else:
                st.info("KPI analysis results missing required columns. Run KPI analysis first.")
        
        else:
            st.info("""
            **Social Media Sentiment Analysis**
            
            After running KPI analysis above, you'll be able to:
            - Analyze sentiment for your top-performing tickers
            - Get insights from X (Twitter), Reddit, and StockTwits
            - Export combined KPI + sentiment results
            - Make data-driven investment decisions
            
            **Setup Required**: Configure API keys for real social media data.
            """)
    
    except Exception as e:
        st.error(f"❌ Error in sentiment analysis section: {e}")
        st.info("For troubleshooting help, see the API Setup & Troubleshooting section above.")
