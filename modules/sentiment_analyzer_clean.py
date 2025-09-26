"""
Clean Sentiment Analyzer Module for Btock Stock KPI Scoring Dashboard
Operates in clear single modes: either real API data or demo mode (no mixing)
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
import random


class SentimentAnalyzer:
    """Handles sentiment analysis with clear single-mode operation"""
    
    def __init__(self):
        """Initialize the sentiment analyzer with API configurations"""
        self.setup_apis()
        self.demo_mode = self._determine_mode()
    
    def setup_apis(self):
        """Setup API connections for X, Reddit, and StockTwits"""
        try:
            # X (Twitter) via Grok API setup
            self.xai_api_key = os.getenv("XAI_API_KEY")
            self.xai_api_url = os.getenv("XAI_API_URL", "https://api.x.ai/v1/chat/completions")
            
            # Reddit API setup
            self.reddit = None
            if all([os.getenv("REDDIT_CLIENT_ID"), os.getenv("REDDIT_CLIENT_SECRET")]):
                try:
                    self.reddit = praw.Reddit(
                        client_id=os.getenv("REDDIT_CLIENT_ID"),
                        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                        user_agent=os.getenv("REDDIT_USER_AGENT", "Btock Sentiment Analyzer v1.0")
                    )
                except Exception as e:
                    self.reddit = None
            
            # StockTwits API (public, no key required)
            self.stocktwits_base_url = "https://api.stocktwits.com/api/2"
            
        except Exception as e:
            st.error(f"Error setting up APIs: {str(e)}")
    
    def _determine_mode(self) -> bool:
        """
        Determine if we should operate in demo mode or real API mode
        Returns True for demo mode, False for real API mode
        """
        # Check if we have at least one working API
        has_x_api = bool(self.xai_api_key)
        has_reddit_api = self.reddit is not None
        
        # If no APIs are configured, use demo mode
        if not has_x_api and not has_reddit_api:
            return True
        
        # Test if configured APIs actually work
        working_apis = 0
        
        if has_x_api:
            try:
                # Quick test of X API
                headers = {"Authorization": f"Bearer {self.xai_api_key}", "Content-Type": "application/json"}
                payload = {"model": "grok-beta", "messages": [{"role": "user", "content": "test"}], "max_tokens": 1}
                response = requests.post(self.xai_api_url, headers=headers, json=payload, timeout=5)
                if response.status_code == 200:
                    working_apis += 1
            except:
                pass
        
        if has_reddit_api:
            try:
                # Quick test of Reddit API
                list(self.reddit.subreddit("test").hot(limit=1))
                working_apis += 1
            except:
                pass
        
        # Use real mode only if we have at least one working API
        return working_apis == 0
    
    def get_sentiment_for_tickers(self, tickers: List[str], hours_back: int = 24) -> pd.DataFrame:
        """
        Get sentiment analysis for multiple tickers in single mode
        """
        results = []
        
        # Show clear mode indication
        if self.demo_mode:
            st.info("🎯 **Demo Mode**: Using simulated sentiment data for demonstration purposes. Configure API keys for real social media data.")
        else:
            st.success("🚀 **Live Mode**: Using real social media data from configured APIs.")
        
        # Calculate time range
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        for ticker in tickers:
            st.write(f"Analyzing sentiment for {ticker}...")
            
            if self.demo_mode:
                # Demo mode: use consistent simulated data
                x_sentiment, reddit_sentiment, stocktwits_sentiment = self._get_demo_sentiment(ticker)
            else:
                # Real mode: use actual APIs
                x_sentiment = self._get_x_sentiment_real(ticker, start_time, end_time)
                reddit_sentiment = self._get_reddit_sentiment_real(ticker, start_time, end_time)
                stocktwits_sentiment = self._get_stocktwits_sentiment_real(ticker, start_time, end_time)
            
            # Calculate total sentiment
            total_sentiment = x_sentiment + reddit_sentiment + stocktwits_sentiment
            
            results.append({
                'Ticker': ticker,
                'X': x_sentiment,
                'Reddit': reddit_sentiment,
                'StockTwits': stocktwits_sentiment,
                'SentimentTotal': total_sentiment
            })
            
            # Small delay between tickers
            time.sleep(0.3)
        
        return pd.DataFrame(results)
    
    def _get_demo_sentiment(self, ticker: str) -> tuple:
        """
        Generate consistent demo sentiment data for a ticker
        Returns (x_sentiment, reddit_sentiment, stocktwits_sentiment)
        """
        # Use ticker hash for consistent results
        seed = hash(ticker) % 1000
        random.seed(seed)
        
        # Generate realistic sentiment patterns
        x_sentiment = random.randint(-2, 3)  # X tends to be more volatile
        reddit_sentiment = random.randint(-1, 2)  # Reddit more discussion-based
        stocktwits_sentiment = random.randint(0, 3)  # StockTwits investor-focused, slight positive bias
        
        # Add some correlation (if one is very positive, others might be too)
        if x_sentiment >= 2:
            reddit_sentiment = max(0, reddit_sentiment)
            stocktwits_sentiment = max(1, stocktwits_sentiment)
        elif x_sentiment <= -1:
            reddit_sentiment = min(0, reddit_sentiment)
            stocktwits_sentiment = max(0, stocktwits_sentiment - 1)
        
        return x_sentiment, reddit_sentiment, stocktwits_sentiment
    
    def _get_x_sentiment_real(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """Get real sentiment from X (Twitter) using Grok API"""
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
            st.warning(f"X API error for {ticker}: {str(e)}")
            return 0
    
    def _get_reddit_sentiment_real(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """Get real sentiment from Reddit"""
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
            st.warning(f"Reddit API error for {ticker}: {str(e)}")
            return 0
    
    def _get_stocktwits_sentiment_real(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """Get real sentiment from StockTwits"""
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
                return 0
                
        except Exception as e:
            st.warning(f"StockTwits API error for {ticker}: {str(e)}")
            return 0
    
    def get_api_status(self) -> Dict[str, bool]:
        """Check the status of all APIs"""
        if self.demo_mode:
            return {"Demo Mode": True, "Real APIs": False}
        else:
            status = {}
            status["X (Grok API)"] = bool(self.xai_api_key)
            status["Reddit"] = self.reddit is not None
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
