"""
Support-Resistance Buy Ranker
==============================

A Python script that ranks stocks based on their proximity to support levels
using technical analysis. Identifies potential buying opportunities by analyzing
support/resistance levels, trend indicators, and momentum.

Usage:
    python sr_ranker.py

Output:
    - Console table with ranked results
    - CSV file: sr_ranked_results.csv
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import numpy as np
import yfinance as yf


# Ticker list to analyze
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD", "INTC", "NFLX",
    "DIS", "BA", "JPM", "BAC", "GS", "WMT", "HD", "NKE", "MCD", "SBUX",
    "PFE", "JNJ", "UNH", "CVX", "XOM", "T", "VZ", "CSCO", "ORCL", "CRM"
]


@dataclass
class Row:
    """Data structure for analysis results"""
    ticker: str
    support: float
    resistance: float
    current_price: float
    ratio: float
    trend: float
    rsi: float
    verdict: str


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index using exponential weighted moving average.
    
    Args:
        series: Price series (typically Close prices)
        period: RSI period (default: 14)
    
    Returns:
        Series containing RSI values (0-100 scale)
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Use exponential weighted moving average
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    
    # Avoid division by zero
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_values = 100 - (100 / (1 + rs))
    
    return rsi_values


def ema(series: pd.Series, span: int) -> pd.Series:
    """
    Calculate Exponential Moving Average.
    
    Args:
        series: Price series
        span: EMA span/period
    
    Returns:
        Series containing EMA values
    """
    return series.ewm(span=span, adjust=False).mean()


def local_extrema(prices: pd.Series, window: int = 5) -> tuple[pd.Series, pd.Series]:
    """
    Identify local extrema (swing highs and lows) using a rolling window approach.
    
    Args:
        prices: Price series
        window: Window size for detecting extrema (default: 5)
    
    Returns:
        Tuple of (local_mins, local_maxs) as boolean Series
    """
    local_mins = pd.Series(False, index=prices.index)
    local_maxs = pd.Series(False, index=prices.index)
    
    for i in range(window, len(prices) - window):
        # Get window slice once for efficiency
        window_slice = prices.iloc[i-window:i+window+1]
        current_price = prices.iloc[i]
        # Get immediate neighbors
        prev_price = prices.iloc[i-1]
        next_price = prices.iloc[i+1]
        
        # Check if current point is a strict local minimum
        if current_price < prev_price and current_price < next_price:
            local_mins.iloc[i] = True
        
        # Check if current point is a strict local maximum
        if current_price > prev_price and current_price > next_price:
            local_maxs.iloc[i] = True
    
    return local_mins, local_maxs


def swing_levels(prices: pd.Series, window: int = 5, k: int = 3) -> tuple[float, float]:
    """
    Calculate support and resistance levels from swing highs and lows.
    
    Args:
        prices: Price series
        window: Window size for detecting swings (default: 5)
        k: Number of recent swings to use for median calculation (default: 3)
    
    Returns:
        Tuple of (support_level, resistance_level)
    """
    local_mins, local_maxs = local_extrema(prices, window)
    
    # Extract actual swing values
    swing_lows = prices[local_mins]
    swing_highs = prices[local_maxs]
    
    # Get the most recent 20 swings (or all if less than 20)
    recent_lows = swing_lows.tail(20)
    recent_highs = swing_highs.tail(20)
    
    # Calculate support and resistance as median of k most recent swings
    if len(recent_lows) >= k:
        support = recent_lows.tail(k).median()
    else:
        support = recent_lows.median() if len(recent_lows) > 0 else prices.min()
    
    if len(recent_highs) >= k:
        resistance = recent_highs.tail(k).median()
    else:
        resistance = recent_highs.median() if len(recent_highs) > 0 else prices.max()
    
    # Fallback to 52-week high/low range if degenerate results
    if pd.isna(support) or pd.isna(resistance) or support >= resistance:
        support = prices.min()
        resistance = prices.max()
    
    # Adjust if current price falls outside the calculated range
    current_price = prices.iloc[-1]
    if current_price < support:
        support = prices.tail(60).min()  # Use recent low
    if current_price > resistance:
        resistance = prices.tail(60).max()  # Use recent high
    
    return support, resistance


def determine_verdict(ratio: float, trend: float, rsi_value: float) -> str:
    """
    Determine buy/watch/avoid verdict based on technical indicators.
    
    Args:
        ratio: Position ratio (0.0 = at support, 1.0 = at resistance)
        trend: Trend indicator (EMA50 - EMA200)
        rsi_value: RSI momentum value (0-100)
    
    Returns:
        Verdict string: "Buy zone ✅", "Watch ⚠️", or "Avoid ❌"
    """
    if ratio <= 0.35 and trend >= 0 and 35 <= rsi_value <= 60:
        return "Buy zone ✅"
    elif ratio <= 0.55 and trend >= 0:
        return "Watch ⚠️"
    else:
        return "Avoid ❌"


def analyze_ticker(ticker: str, start_date: datetime) -> Optional[Row]:
    """
    Analyze a single ticker for support/resistance buying opportunities.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date for fetching historical data
    
    Returns:
        Row object with analysis results, or None if analysis fails
    """
    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date)
        
        if df.empty or len(df) < 60:
            print(f"⚠️  {ticker}: Insufficient data (got {len(df)} days)")
            return None
        
        prices = df['Close']
        
        # Calculate support and resistance
        support, resistance = swing_levels(prices, window=5, k=3)
        
        # Calculate current position ratio
        current_price = prices.iloc[-1]
        
        if resistance == support:
            # Avoid division by zero
            position_ratio = 0.5
        else:
            position_ratio = (current_price - support) / (resistance - support)
        
        # Calculate trend (50 EMA - 200 EMA)
        ema50 = ema(prices, 50)
        
        # Use 200 EMA if sufficient data, otherwise use shorter period
        if len(prices) >= 200:
            ema200 = ema(prices, 200)
        else:
            ema200 = ema(prices, min(len(prices) // 2, 100))
        
        trend = ema50.iloc[-1] - ema200.iloc[-1]
        
        # Calculate RSI
        rsi_values = rsi(prices, period=14)
        current_rsi = rsi_values.iloc[-1]
        
        # Determine verdict using helper function
        verdict = determine_verdict(position_ratio, trend, current_rsi)
        
        return Row(
            ticker=ticker,
            support=round(support, 2),
            resistance=round(resistance, 2),
            current_price=round(current_price, 2),
            ratio=round(position_ratio, 2),
            trend=round(trend, 2),
            rsi=round(current_rsi, 1),
            verdict=verdict
        )
        
    except Exception as e:
        print(f"❌ {ticker}: Error - {str(e)}")
        return None


def main():
    """
    Main function to orchestrate the stock analysis and ranking process.
    """
    print("=" * 80)
    print("Support-Resistance Buy Ranker".center(80))
    print("=" * 80)
    print()
    
    # Calculate start date (12 months = 370 days ago)
    start_date = datetime.now() - timedelta(days=370)
    
    print(f"📅 Fetching data from {start_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🔍 Analyzing {len(TICKERS)} tickers...")
    print()
    
    results = []
    
    # Analyze each ticker
    for ticker in TICKERS:
        result = analyze_ticker(ticker, start_date)
        if result:
            results.append(result)
    
    if not results:
        print("❌ No data returned for any ticker")
        return
    
    # Convert to DataFrame for easy sorting and display
    df = pd.DataFrame([
        {
            'Ticker': r.ticker,
            'Support': r.support,
            'Resistance': r.resistance,
            'Current': r.current_price,
            'Ratio': r.ratio,
            'Trend': r.trend,
            'RSI': r.rsi,
            'Verdict': r.verdict
        }
        for r in results
    ])
    
    # Sort by ratio (ascending - closest to support first), then by trend (descending)
    df = df.sort_values(by=['Ratio', 'Trend'], ascending=[True, False])
    
    # Display results
    print()
    print("=" * 80)
    print("RANKED RESULTS".center(80))
    print("=" * 80)
    print()
    
    # Format and display the table
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    print(df.to_string(index=False))
    
    # Save to CSV
    output_file = "sr_ranked_results.csv"
    df.to_csv(output_file, index=False)
    
    print()
    print("=" * 80)
    print(f"✅ Results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
