"""
Test script for Btock Stock KPI Scoring Dashboard
Tests core functionality without Streamlit UI
"""

import os
import sys
from modules.data_fetcher import DataFetcher
from modules.indicators import TechnicalIndicators
from modules.scoring import ScoringEngine
from modules.utils import WeightValidator

def test_basic_functionality():
    """Test basic functionality of the application"""
    
    print("🧪 Testing Btock Stock KPI Scoring Dashboard")
    print("=" * 50)
    
    # Test data fetcher
    print("1. Testing Data Fetcher...")
    data_fetcher = DataFetcher()
    
    # Test with a simple ticker
    test_ticker = "AAPL"
    print(f"   Fetching data for {test_ticker}...")
    
    stock_data = data_fetcher.fetch_stock_data(test_ticker, period="6mo")
    if stock_data is not None and not stock_data.empty:
        print(f"   ✅ Successfully fetched {len(stock_data)} days of data")
        print(f"   📊 Data range: {stock_data.index[0].date()} to {stock_data.index[-1].date()}")
    else:
        print("   ❌ Failed to fetch stock data")
        return False
    
    # Test current price
    current_price = data_fetcher.get_current_price(test_ticker)
    if current_price:
        print(f"   💰 Current price: ${current_price:.2f}")
    else:
        print("   ⚠️  Could not get current price")
    
    # Test indicators
    print("\n2. Testing Technical Indicators...")
    indicators_calculator = TechnicalIndicators()
    
    indicators = indicators_calculator.calculate_all_indicators(stock_data)
    if indicators:
        print(f"   ✅ Successfully calculated {len(indicators)} indicators")
        
        # Show some key indicators
        key_indicators = ['rsi', 'macd', 'adx', 'atr']
        for indicator in key_indicators:
            if indicator in indicators:
                print(f"   📈 {indicator.upper()}: {indicators[indicator]:.4f}")
    else:
        print("   ❌ Failed to calculate indicators")
        return False
    
    # Test scoring
    print("\n3. Testing Scoring Engine...")
    scoring_engine = ScoringEngine()
    
    # Get default weights
    weights = WeightValidator.get_default_weights()
    print(f"   ⚖️  Using weights: {weights}")
    
    # Analyze ticker
    analysis_result = scoring_engine.analyze_ticker(indicators, weights)
    if analysis_result:
        print("   ✅ Successfully completed analysis")
        print(f"   🎯 Final Score: {analysis_result['final_weighted_score']:.4f}")
        print(f"   📊 Signal: {analysis_result['signal']}")
        
        # Show category scores
        categories = ['momentum_score', 'trend_score', 'volatility_score', 'strength_score', 'support_resistance_score']
        for category in categories:
            if category in analysis_result:
                print(f"   📈 {category.replace('_', ' ').title()}: {analysis_result[category]:.4f}")
    else:
        print("   ❌ Failed to complete analysis")
        return False
    
    # Test database connection (optional)
    print("\n4. Testing Database Connection...")
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        try:
            import psycopg2
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"   ✅ Database connected: {version[0][:50]}...")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"   ⚠️  Database connection issue: {str(e)}")
    else:
        print("   ℹ️  No DATABASE_URL configured (optional for local testing)")
    
    print("\n🎉 All tests completed successfully!")
    print("The application is ready for deployment.")
    return True

if __name__ == "__main__":
    # Set database URL for testing
    if len(sys.argv) > 1:
        os.environ['DATABASE_URL'] = sys.argv[1]
    
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
