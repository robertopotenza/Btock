"""
Production Sentiment Analyzer Module for Btock Stock KPI Scoring Dashboard
Focuses on real API configuration and troubleshooting instead of demo mode
"""

import requests
import praw
from datetime import datetime, timezone, timedelta
import os
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional
import time
import json


class SentimentAnalyzer:
    """Production sentiment analyzer with troubleshooting guidance"""
    
    def __init__(self):
        """Initialize the sentiment analyzer with API configurations"""
        self.setup_apis()
        self.api_status = self.get_api_status()
    
    def setup_apis(self):
        """Setup API connections for X, Reddit, and StockTwits"""
        try:
            # X (Twitter) via Grok API setup
            self.xai_api_key = os.getenv("XAI_API_KEY")
            self.xai_api_url = os.getenv("XAI_API_URL", "https://api.x.ai/v1/chat/completions")
            
            # Reddit API setup
            self.reddit = None
            reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
            reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            
            if reddit_client_id and reddit_client_secret:
                try:
                    # Handle multiple possible user agent environment variable names
                    user_agent = (
                        os.getenv("REDDIT_USER_AGENT") or 
                        os.getenv("user_agent") or 
                        "StockResearchBot/1.0"
                    )
                    
                    self.reddit = praw.Reddit(
                        client_id=reddit_client_id,
                        client_secret=reddit_client_secret,
                        user_agent=user_agent
                    )
                    
                    # Test Reddit connection with a simple, safe call
                    try:
                        # Use a more reliable test - just check if we can access Reddit
                        test_subreddit = self.reddit.subreddit("announcements")
                        # Get just one post to test authentication
                        next(iter(test_subreddit.hot(limit=1)))
                        print(f"✅ Reddit API connected successfully with user agent: {user_agent}")
                    except Exception as test_e:
                        # If test fails, provide specific guidance
                        error_msg = str(test_e).lower()
                        if "401" in error_msg or "unauthorized" in error_msg:
                            guidance = """
Reddit API 401 Error - Authentication Failed:

1. Verify Reddit App Configuration:
   - Go to: https://www.reddit.com/prefs/apps
   - Ensure app type is 'script' (not 'web app')
   - Check Client ID and Secret are correct

2. Current Credentials:
   - Client ID: {}
   - Secret: {} (first 10 chars)
   - User Agent: {}

3. Common Issues:
   - App type must be 'script' for personal use
   - Client ID is the string under your app name
   - Client Secret is the longer string labeled 'secret'
   - Make sure app is not suspended or restricted

4. Fix Steps:
   - Delete current Reddit app and create new one
   - Choose 'script' type when creating
   - Update environment variables with new credentials
                            """.format(
                                reddit_client_id,
                                reddit_client_secret[:10] + "..." if len(reddit_client_secret) > 10 else reddit_client_secret,
                                user_agent
                            )
                            print(guidance)
                            if hasattr(st, 'error'):
                                st.error("Reddit API Authentication Failed (401)")
                                st.info("Check the console/logs for detailed troubleshooting steps.")
                        else:
                            print(f"Reddit API test failed: {test_e}")
                            if hasattr(st, 'warning'):
                                st.warning(f"Reddit API test failed: {test_e}")
                        
                        self.reddit = None
                        
                except Exception as e:
                    print(f"Reddit API setup failed: {str(e)}")
                    if hasattr(st, 'warning'):
                        st.warning(f"Reddit API setup failed: {str(e)}")
                    self.reddit = None
            else:
                print("Reddit API credentials not found - set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
            
            # StockTwits API (public, no key required)
            self.stocktwits_base_url = "https://api.stocktwits.com/api/2"
            
        except Exception as e:
            st.error(f"Error setting up APIs: {str(e)}")
    
    def get_sentiment_for_tickers(self, tickers: List[str], hours_back: int = 24) -> pd.DataFrame:
        """
        Get sentiment analysis for multiple tickers with troubleshooting guidance
        """
        # Check API configuration first
        working_apis = [name for name, status in self.api_status.items() if status]
        
        if not working_apis:
            self._show_api_setup_guidance()
            return pd.DataFrame()  # Return empty DataFrame
        
        # Show which APIs are working
        st.success(f"🚀 **Using APIs**: {', '.join(working_apis)}")
        
        results = []
        
        # Calculate time range
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        for ticker in tickers:
            st.write(f"Analyzing sentiment for {ticker}...")
            
            # Get sentiment from each platform
            x_sentiment = self._get_x_sentiment(ticker, start_time, end_time)
            reddit_sentiment = self._get_reddit_sentiment(ticker, start_time, end_time)
            stocktwits_sentiment = self._get_stocktwits_sentiment(ticker, start_time, end_time)
            
            # Calculate total sentiment
            total_sentiment = x_sentiment + reddit_sentiment + stocktwits_sentiment
            
            results.append({
                'Ticker': ticker,
                'X': x_sentiment,
                'Reddit': reddit_sentiment,
                'StockTwits': stocktwits_sentiment,
                'SentimentTotal': total_sentiment
            })
            
            # Small delay between tickers to avoid rate limiting
            time.sleep(0.5)
        
        return pd.DataFrame(results)
    
    def _show_api_setup_guidance(self):
        """Show comprehensive API setup guidance"""
        st.error("🔧 **API Configuration Required**")
        
        st.markdown("""
        **To use sentiment analysis, configure at least one API:**
        
        ### 🐦 X (Twitter) via Grok API
        ```bash
        # Set in Railway Dashboard → Variables
        XAI_API_KEY=your_grok_api_key
        ```
        - Get API key from: https://x.ai/
        - Test endpoint: https://api.x.ai/v1/chat/completions
        
        ### 🔴 Reddit API  
        ```bash
        # Set in Railway Dashboard → Variables
        REDDIT_CLIENT_ID=your_reddit_client_id
        REDDIT_CLIENT_SECRET=your_reddit_client_secret
        REDDIT_USER_AGENT=Btock Sentiment Analyzer v1.0
        ```
        - Create app at: https://www.reddit.com/prefs/apps
        - Choose "script" type application
        
        ### 📈 StockTwits API
        - No setup required (public API)
        - May have rate limits without authentication
        """)
        
        # Show current status
        st.subheader("🔍 Current API Status")
        status_df = pd.DataFrame([
            {"API": "X (Grok)", "Status": "❌ Not Configured" if not self.xai_api_key else "⚠️ Needs Testing"},
            {"API": "Reddit", "Status": "❌ Not Configured" if not self.reddit else "✅ Configured"},
            {"API": "StockTwits", "Status": "✅ Available (Public API)"}
        ])
        st.dataframe(status_df, width='stretch')
        
        # Troubleshooting steps
        with st.expander("🐛 Troubleshooting Steps"):
            st.markdown("""
            ### **Step 1: Set Environment Variables**
            1. Go to Railway Dashboard → Your Project → Variables
            2. Add the API keys listed above
            3. Click "Deploy" to restart the application
            
            ### **Step 2: Test API Keys**
            **Test Grok API:**
            ```bash
            curl -H "Authorization: Bearer YOUR_API_KEY" \\
                 -H "Content-Type: application/json" \\
                 -d '{"model":"grok-beta","messages":[{"role":"user","content":"test"}],"max_tokens":1}' \\
                 https://api.x.ai/v1/chat/completions
            ```
            
            **Test Reddit API:**
            - Verify app type is "script" 
            - Check client ID and secret are correct
            - Ensure app is not suspended
            
            ### **Step 3: Common Issues**
            - **404 Errors**: Check API endpoint URL and key validity
            - **403 Errors**: Rate limiting or authentication issues
            - **Demo Mode**: Environment variables not set or app not restarted
            
            ### **Step 4: Verify Deployment**
            - Check Railway deployment logs for errors
            - Restart application after setting variables
            - Test sentiment analysis after deployment
            """)
    
    def _get_x_sentiment(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """Get sentiment from X (Twitter) using Grok API"""
        try:
            if not self.xai_api_key:
                return 0
            
            prompt = f"Analyze recent X posts about ${ticker} stock. Count positive vs negative sentiment mentions. Return format: 'positive: X, negative: Y'"
            
            headers = {
                "Authorization": f"Bearer {self.xai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.1
            }
            
            response = requests.post(self.xai_api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"].lower()
            
            # Parse response
            positive = 0
            negative = 0
            
            try:
                if "positive:" in content:
                    positive = int(content.split("positive:")[1].split(",")[0].strip())
                if "negative:" in content:
                    negative = int(content.split("negative:")[1].split(",")[0].strip())
            except:
                pass
            
            return positive - negative
            
        except Exception as e:
            st.warning(f"X sentiment analysis failed for {ticker}: {str(e)}")
            return 0
    
    def _get_reddit_sentiment(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """Get sentiment from Reddit"""
        try:
            if not self.reddit:
                return 0
            
            subreddits = ["stocks", "investing", "SecurityAnalysis", "StockMarket"]
            total_score = 0
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    for submission in subreddit.search(f"${ticker} OR {ticker}", limit=5):
                        created_time = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
                        
                        if start_time <= created_time <= end_time:
                            text = (submission.title + " " + submission.selftext).lower()
                            
                            positive_words = ["buy", "bullish", "up", "good", "great", "strong", "positive"]
                            negative_words = ["sell", "bearish", "down", "bad", "weak", "negative", "drop"]
                            
                            pos_count = sum(1 for word in positive_words if word in text)
                            neg_count = sum(1 for word in negative_words if word in text)
                            
                            if pos_count > neg_count:
                                total_score += 1
                            elif neg_count > pos_count:
                                total_score -= 1
                    
                    time.sleep(0.2)
                    
                except Exception:
                    continue
            
            return total_score
            
        except Exception as e:
            st.warning(f"Reddit sentiment analysis failed for {ticker}: {str(e)}")
            return 0
    
    def _get_stocktwits_sentiment(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """Get sentiment from StockTwits"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            url = f"{self.stocktwits_base_url}/streams/symbol/{ticker}.json"
            response = requests.get(url, params={"limit": 20}, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                score = 0
                for message in messages:
                    try:
                        entities = message.get("entities", {})
                        sentiment_data = entities.get("sentiment", {})
                        
                        if sentiment_data:
                            if sentiment_data.get("basic") == "Bullish":
                                score += 1
                            elif sentiment_data.get("basic") == "Bearish":
                                score -= 1
                    except:
                        continue
                
                return score
            else:
                st.warning(f"StockTwits API returned status {response.status_code} for {ticker}")
                return 0
                
        except Exception as e:
            st.warning(f"StockTwits sentiment analysis failed for {ticker}: {str(e)}")
            return 0
    
    def get_api_status(self) -> Dict[str, bool]:
        """Check the status of all APIs"""
        status = {}
        
        # Check X API
        status["X (Grok API)"] = bool(self.xai_api_key)
        
        # Check Reddit API
        status["Reddit"] = self.reddit is not None
        
        # Check StockTwits (always available as public API)
        status["StockTwits"] = True
        
        return status
    
    def format_sentiment_results(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """Format sentiment results for display"""
        if results_df.empty:
            return results_df
        
        # Add sentiment interpretation
        def interpret_sentiment(score):
            if score >= 5:
                return "🟢 Very Positive"
            elif score >= 2:
                return "🟡 Positive"
            elif score >= -1:
                return "⚪ Neutral"
            elif score >= -3:
                return "🟠 Negative"
            else:
                return "🔴 Very Negative"
        
        formatted_df = results_df.copy()
        formatted_df['Sentiment'] = formatted_df['SentimentTotal'].apply(interpret_sentiment)
        
        # Reorder columns
        column_order = ['Ticker', 'X', 'Reddit', 'StockTwits', 'SentimentTotal', 'Sentiment']
        formatted_df = formatted_df[column_order]
        
        return formatted_df
