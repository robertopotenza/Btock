"""
Btock Stock Analysis Dashboard
Main Application Hub

Choose between KPI Scoring (technical indicators) and Sentiment Analysis (social media sentiment).
Both tools can be used independently or chained together for comprehensive stock analysis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Btock Stock Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tool-card {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .tool-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.15);
    }
    .tool-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .feature-list {
        margin: 1rem 0;
    }
    .feature-item {
        margin: 0.5rem 0;
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application hub"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Btock Stock Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; font-size: 1.2rem; margin-bottom: 3rem; color: #6c757d;">
    Comprehensive stock analysis using technical indicators and social media sentiment
    </div>
    """, unsafe_allow_html=True)
    
    # Tool selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">📈 KPI Scoring Dashboard</div>
            <p><strong>Technical Indicator Analysis</strong></p>
            <p>Evaluate stocks using 11+ technical indicators across 5 categories with weighted scoring system.</p>
            
            <div class="feature-list">
                <div class="feature-item">✅ RSI, MACD, ADX, ATR, Moving Averages</div>
                <div class="feature-item">✅ CCI, Stochastic, Williams %R, ROC</div>
                <div class="feature-item">✅ Ultimate Oscillator, Pivot Points</div>
                <div class="feature-item">✅ Weighted scoring with BUY/HOLD/SELL signals</div>
                <div class="feature-item">✅ Excel export with formatting</div>
                <div class="feature-item">✅ Database persistence</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch KPI Scoring", type="primary", use_container_width=True):
            st.switch_page("kpi_app.py")
    
    with col2:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">📊 Sentiment Scoring Dashboard</div>
            <p><strong>Social Media Sentiment Analysis</strong></p>
            <p>Analyze sentiment from X (Twitter), Reddit, and StockTwits using raw count methodology.</p>
            
            <div class="feature-list">
                <div class="feature-item">✅ X (Twitter) via Grok API</div>
                <div class="feature-item">✅ Reddit sentiment analysis</div>
                <div class="feature-item">✅ StockTwits public API</div>
                <div class="feature-item">✅ Raw count scoring (+1/-1/0)</div>
                <div class="feature-item">✅ Configurable time ranges</div>
                <div class="feature-item">✅ Integration with KPI results</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch Sentiment Analysis", type="primary", use_container_width=True):
            st.switch_page("sentiment_app.py")
    
    # Workflow section
    st.markdown("---")
    st.subheader("🔄 Recommended Workflow")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Option 1: KPI Only**
        
        1. Upload ticker list
        2. Configure weights
        3. Run technical analysis
        4. Get BUY/HOLD/SELL signals
        5. Export results
        """)
    
    with col2:
        st.markdown("""
        **Option 2: Sentiment Only**
        
        1. Enter tickers manually
        2. Set time range
        3. Run sentiment analysis
        4. Get social media insights
        5. Export results
        """)
    
    with col3:
        st.markdown("""
        **Option 3: Combined Analysis**
        
        1. Run KPI Scoring first
        2. Extract top 10 performers
        3. Run Sentiment Analysis
        4. Get comprehensive insights
        5. Make informed decisions
        """)
    
    # Integration info
    st.markdown("---")
    st.subheader("🔗 Tool Integration")
    
    # Check if there are results from previous analyses
    kpi_results_available = 'kpi_results' in st.session_state
    sentiment_results_available = 'sentiment_results' in st.session_state
    
    if kpi_results_available or sentiment_results_available:
        st.success("✅ Previous analysis results detected!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if kpi_results_available:
                kpi_time = st.session_state.get('kpi_analysis_time', 'Unknown')
                st.info(f"📈 **KPI Results Available**\nAnalyzed: {kmp_time}")
                
                if st.button("View KPI Results"):
                    st.dataframe(st.session_state['kpi_results'])
        
        with col2:
            if sentiment_results_available:
                st.info("📊 **Sentiment Results Available**")
                
                if st.button("View Sentiment Results"):
                    st.dataframe(st.session_state['sentiment_results'])
    
    else:
        st.info("💡 **Tip:** Results from each tool are automatically saved for integration. Run KPI Scoring first, then use the top performers for Sentiment Analysis.")
    
    # API Configuration section
    st.markdown("---")
    st.subheader("⚙️ API Configuration")
    
    with st.expander("🔧 Required Environment Variables"):
        st.markdown("""
        **For Sentiment Analysis:**
        
        ```bash
        # X (Twitter) via Grok API
        XAI_API_KEY=your_grok_api_key
        XAI_API_URL=https://api.x.ai/v1/chat/completions
        
        # Reddit API
        REDDIT_CLIENT_ID=your_reddit_client_id
        REDDIT_CLIENT_SECRET=your_reddit_client_secret
        REDDIT_USER_AGENT=Btock Sentiment Analyzer v1.0
        
        # StockTwits (no API key required - public API)
        ```
        
        **For Database (Optional):**
        
        ```bash
        # PostgreSQL Database
        DATABASE_URL=postgresql://user:password@host:port/database
        ```
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; margin-top: 2rem;">
    <p><strong>Btock Stock Analysis Dashboard</strong> - Comprehensive Technical and Sentiment Analysis</p>
    <p>Built with Streamlit • Powered by Yahoo Finance, Grok API, Reddit API, and StockTwits</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
