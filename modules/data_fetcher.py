"""
Data Fetcher Module for Btock Stock KPI Scoring Dashboard
Handles Yahoo Finance data retrieval and validation
"""

import yfinance as yf
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional, Tuple
import time
from datetime import datetime, timedelta


class DataFetcher:
    """Handles stock data fetching from Yahoo Finance"""
    
    def __init__(self):
        self.cache_duration = 3600  # 1 hour cache
    
    @st.cache_data(ttl=3600)
    def fetch_stock_data(_self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data for a single ticker
        
        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            stock = yf.Ticker(ticker.upper())
            data = stock.history(period=period)
            
            if data.empty:
                return None
                
            # Ensure we have required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_columns):
                return None
                
            return data
            
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker exists and has data
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if ticker is valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            # Check if ticker has basic info
            if not info or 'symbol' not in info:
                return False
                
            # Try to get recent data
            data = stock.history(period="5d")
            return not data.empty
            
        except:
            return False
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current/latest price for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Current price or None if error
        """
        try:
            stock = yf.Ticker(ticker.upper())
            data = stock.history(period="1d")
            
            if data.empty:
                return None
                
            return float(data['Close'].iloc[-1])
            
        except:
            return None
    
    def batch_fetch_data(self, tickers: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple tickers with progress tracking
        
        Args:
            tickers: List of ticker symbols
            period: Data period
            
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_tickers = len(tickers)
        
        for i, ticker in enumerate(tickers):
            # Update progress
            progress = (i + 1) / total_tickers
            progress_bar.progress(progress)
            status_text.text(f"Fetching data for {ticker.upper()} ({i + 1}/{total_tickers})")
            
            # Fetch data
            data = self.fetch_stock_data(ticker, period)
            if data is not None:
                results[ticker.upper()] = data
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return results
    
    def get_ticker_info(self, ticker: str) -> Dict:
        """
        Get basic ticker information
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with ticker info
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            return {
                'symbol': info.get('symbol', ticker.upper()),
                'longName': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'marketCap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD')
            }
            
        except:
            return {
                'symbol': ticker.upper(),
                'longName': 'N/A',
                'sector': 'N/A',
                'industry': 'N/A',
                'marketCap': 0,
                'currency': 'USD'
            }
    
    def validate_tickers_batch(self, tickers: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate a batch of tickers
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Tuple of (valid_tickers, invalid_tickers)
        """
        valid_tickers = []
        invalid_tickers = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_tickers = len(tickers)
        
        for i, ticker in enumerate(tickers):
            # Update progress
            progress = (i + 1) / total_tickers
            progress_bar.progress(progress)
            status_text.text(f"Validating {ticker.upper()} ({i + 1}/{total_tickers})")
            
            if self.validate_ticker(ticker):
                valid_tickers.append(ticker.upper())
            else:
                invalid_tickers.append(ticker.upper())
            
            # Small delay
            time.sleep(0.05)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return valid_tickers, invalid_tickers
