"""
Sentiment Analyzer Module for Btock Stock KPI Scoring Dashboard
Handles sentiment analysis from X (Twitter), Reddit, and StockTwits
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
    """Handles sentiment analysis from multiple social media platforms"""
    
    def __init__(self):
        """Initialize the sentiment analyzer with API configurations"""
        self.setup_apis()
    
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
                    st.warning(f"Reddit API setup failed: {str(e)}")
            
            # StockTwits API (public, no key required)
            self.stocktwits_base_url = "https://api.stocktwits.com/api/2"
            
        except Exception as e:
            st.error(f"Error setting up APIs: {str(e)}")
    
    def get_sentiment_for_tickers(self, tickers: List[str], hours_back: int = 24) -> pd.DataFrame:
        """
        Get sentiment scores for a list of tickers from multiple platforms
        
        Args:
            tickers: List of ticker symbols
            hours_back: Number of hours to look back for sentiment data
            
        Returns:
            DataFrame with sentiment scores for each ticker
        """
        try:
            # Calculate time range
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours_back)
            
            st.info(f"Analyzing sentiment for {len(tickers)} tickers over the last {hours_back} hours...")
            
            results = []
            progress_bar = st.progress(0)
            
            for i, ticker in enumerate(tickers):
                st.write(f"Analyzing sentiment for {ticker}...")
                
                # Get sentiment from each platform
                x_sentiment = self._get_x_sentiment(ticker, start_time, end_time)
                reddit_sentiment = self._get_reddit_sentiment(ticker, start_time, end_time)
                stocktwits_sentiment = self._get_stocktwits_sentiment(ticker, start_time, end_time)
                
                # Calculate total sentiment
                sentiment_total = x_sentiment + reddit_sentiment + stocktwits_sentiment
                
                results.append({
                    "Ticker": ticker,
                    "X": x_sentiment,
                    "Reddit": reddit_sentiment,
                    "StockTwits": stocktwits_sentiment,
                    "SentimentTotal": sentiment_total
                })
                
                # Update progress
                progress_bar.progress((i + 1) / len(tickers))
                
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
            
            progress_bar.empty()
            return pd.DataFrame(results)
            
        except Exception as e:
            st.error(f"Error analyzing sentiment: {str(e)}")
            return pd.DataFrame()
    
    def _get_x_sentiment(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """
        Get sentiment from X (Twitter) using Grok API
        
        Args:
            ticker: Stock ticker symbol
            start_time: Start time for analysis
            end_time: End time for analysis
            
        Returns:
            Net sentiment score (positive - negative)
        """
        try:
            if not self.xai_api_key:
                return 0
            
            prompt = (
                f"Search X for posts mentioning '${ticker}' or '{ticker} stock' "
                f"from {start_time.isoformat()}Z to {end_time.isoformat()}Z in English, "
                "excluding retweets. Classify each post strictly as positive, negative, or neutral. "
                "Return only counts in format: 'positive: X, negative: Y, neutral: Z'"
            )
            
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
            
            # Parse the response to extract counts
            positive = 0
            negative = 0
            
            if "positive:" in content:
                try:
                    positive = int(content.split("positive:")[1].split(",")[0].strip())
                except:
                    pass
            
            if "negative:" in content:
                try:
                    negative = int(content.split("negative:")[1].split(",")[0].strip())
                except:
                    pass
            
            return positive - negative
            
        except Exception as e:
            st.warning(f"X sentiment analysis failed for {ticker}: {str(e)}")
            return 0
    
    def _get_reddit_sentiment(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """
        Get sentiment from Reddit
        
        Args:
            ticker: Stock ticker symbol
            start_time: Start time for analysis
            end_time: End time for analysis
            
        Returns:
            Net sentiment score
        """
        try:
            if not self.reddit:
                return 0
            
            subreddits = ["stocks", "wallstreetbets", "investing", "SecurityAnalysis"]
            total_score = 0
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for posts mentioning the ticker
                    for post in subreddit.search(ticker, limit=20, sort="new"):
                        created_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                        
                        if start_time <= created_time <= end_time:
                            text = (post.title + " " + post.selftext).lower()
                            
                            # Simple sentiment analysis based on keywords
                            bullish_words = ["buy", "bull", "bullish", "up", "moon", "rocket", "calls", "long"]
                            bearish_words = ["sell", "bear", "bearish", "down", "crash", "puts", "short"]
                            
                            bullish_count = sum(1 for word in bullish_words if word in text)
                            bearish_count = sum(1 for word in bearish_words if word in text)
                            
                            if bullish_count > bearish_count:
                                total_score += 1
                            elif bearish_count > bullish_count:
                                total_score -= 1
                    
                    # Small delay between subreddit requests
                    time.sleep(0.2)
                    
                except Exception as e:
                    continue
            
            return total_score
            
        except Exception as e:
            st.warning(f"Reddit sentiment analysis failed for {ticker}: {str(e)}")
            return 0
    
    def _get_stocktwits_sentiment(self, ticker: str, start_time: datetime, end_time: datetime) -> int:
        """
        Get sentiment from StockTwits
        
        Args:
            ticker: Stock ticker symbol
            start_time: Start time for analysis
            end_time: End time for analysis
            
        Returns:
            Net sentiment score
        """
        try:
            url = f"{self.stocktwits_base_url}/streams/symbol/{ticker}.json"
            
            response = requests.get(url, params={"limit": 30}, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            messages = data.get("messages", [])
            
            score = 0
            
            for message in messages:
                try:
                    # Parse creation time
                    created_at = message.get("created_at", "")
                    if created_at:
                        # StockTwits format: "2024-01-01T12:00:00Z"
                        created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        
                        if start_time <= created_time <= end_time:
                            # Get sentiment from StockTwits API
                            entities = message.get("entities", {})
                            sentiment_data = entities.get("sentiment", {})
                            basic_sentiment = sentiment_data.get("basic", "neutral")
                            
                            if basic_sentiment == "Bullish":
                                score += 1
                            elif basic_sentiment == "Bearish":
                                score -= 1
                
                except Exception:
                    continue
            
            return score
            
        except Exception as e:
            st.warning(f"StockTwits sentiment analysis failed for {ticker}: {str(e)}")
            return 0
    
    def get_api_status(self) -> Dict[str, bool]:
        """
        Check the status of all APIs
        
        Returns:
            Dictionary with API status
        """
        status = {
            "X (Grok API)": bool(self.xai_api_key),
            "Reddit": self.reddit is not None,
            "StockTwits": True  # Public API, always available
        }
        
        return status
    
    def format_sentiment_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format sentiment results for display
        
        Args:
            df: Raw sentiment results DataFrame
            
        Returns:
            Formatted DataFrame
        """
        try:
            if df.empty:
                return df
            
            # Sort by SentimentTotal (highest first)
            df_formatted = df.sort_values("SentimentTotal", ascending=False).reset_index(drop=True)
            
            # Add sentiment interpretation
            def interpret_sentiment(score):
                if score > 2:
                    return "🟢 Very Positive"
                elif score > 0:
                    return "🟡 Positive"
                elif score == 0:
                    return "⚪ Neutral"
                elif score > -3:
                    return "🟠 Negative"
                else:
                    return "🔴 Very Negative"
            
            df_formatted["Sentiment"] = df_formatted["SentimentTotal"].apply(interpret_sentiment)
            
            return df_formatted
            
        except Exception as e:
            st.error(f"Error formatting sentiment results: {str(e)}")
            return df
