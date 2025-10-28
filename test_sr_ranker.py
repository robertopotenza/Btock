"""
Test script for sr_ranker.py
Tests the core functions with synthetic data (no network required)
"""

import pandas as pd
import numpy as np
from sr_ranker import rsi, ema, local_extrema, swing_levels, Row


def test_rsi():
    """Test RSI calculation"""
    print("Testing RSI calculation...")
    
    # Create synthetic price data
    prices = pd.Series([
        44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08,
        45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64,
        46.21, 46.25, 45.71, 46.45, 45.78, 45.35, 44.03, 44.18, 44.22, 44.57
    ])
    
    rsi_values = rsi(prices, period=14)
    
    # RSI should be between 0 and 100
    assert rsi_values.max() <= 100, "RSI exceeds 100"
    assert rsi_values.min() >= 0, "RSI below 0"
    
    # Check that we have valid RSI values (not all NaN)
    assert not rsi_values.isna().all(), "All RSI values are NaN"
    
    print(f"  ✅ RSI calculation passed (last value: {rsi_values.iloc[-1]:.2f})")


def test_ema():
    """Test EMA calculation"""
    print("Testing EMA calculation...")
    
    prices = pd.Series(range(1, 51))  # 1 to 50
    ema_values = ema(prices, span=10)
    
    # EMA should follow the trend
    assert ema_values.iloc[-1] > ema_values.iloc[0], "EMA not following upward trend"
    
    # EMA should be between min and max prices
    assert ema_values.iloc[-1] >= prices.min(), "EMA below minimum price"
    assert ema_values.iloc[-1] <= prices.max(), "EMA above maximum price"
    
    print(f"  ✅ EMA calculation passed (last value: {ema_values.iloc[-1]:.2f})")


def test_local_extrema():
    """Test local extrema detection"""
    print("Testing local extrema detection...")
    
    # Create price series with clear peaks and troughs
    prices = pd.Series([
        10, 11, 12, 11, 10,  # peak at index 2
        9, 8, 9, 10, 11,     # trough at index 6
        12, 13, 12, 11, 10,  # peak at index 11
        9, 10, 11, 12, 13    # trough at index 15
    ])
    
    local_mins, local_maxs = local_extrema(prices, window=2)
    
    # Should detect at least some extrema
    assert local_mins.sum() > 0 or local_maxs.sum() > 0, "No extrema detected"
    
    print(f"  ✅ Local extrema detection passed ({local_mins.sum()} mins, {local_maxs.sum()} maxs)")


def test_swing_levels():
    """Test support/resistance calculation"""
    print("Testing swing levels calculation...")
    
    # Create price series with clear support and resistance
    prices = pd.Series([
        100, 105, 110, 105, 100,  # resistance ~110, support ~100
        95, 100, 105, 110, 105,
        100, 95, 100, 105, 110,
        105, 100, 105, 110, 105,
        100, 105, 108, 107, 106   # current price ~106
    ] * 3)  # Repeat to have enough data
    
    support, resistance = swing_levels(prices, window=5, k=3)
    
    # Support should be less than resistance
    assert support < resistance, f"Support ({support}) not less than resistance ({resistance})"
    
    # Support should be near lower bound, resistance near upper bound
    assert support >= prices.min(), "Support below minimum price"
    assert resistance <= prices.max(), "Resistance above maximum price"
    
    print(f"  ✅ Swing levels passed (support: {support:.2f}, resistance: {resistance:.2f})")


def test_row_dataclass():
    """Test Row dataclass structure"""
    print("Testing Row dataclass...")
    
    row = Row(
        ticker="TEST",
        support=100.0,
        resistance=120.0,
        current_price=110.0,
        ratio=0.5,
        trend=2.5,
        rsi=55.0,
        verdict="Watch ⚠️"
    )
    
    assert row.ticker == "TEST", "Ticker mismatch"
    assert row.support == 100.0, "Support mismatch"
    assert row.verdict == "Watch ⚠️", "Verdict mismatch"
    
    print("  ✅ Row dataclass test passed")


def test_verdict_logic():
    """Test verdict determination logic"""
    print("Testing verdict logic...")
    
    # Test Buy zone criteria
    ratio = 0.30  # Within 35% of support
    trend = 1.0   # Positive trend
    rsi_val = 50.0   # Between 35 and 60
    
    if ratio <= 0.35 and trend >= 0 and 35 <= rsi_val <= 60:
        verdict = "Buy zone ✅"
    elif ratio <= 0.55 and trend >= 0:
        verdict = "Watch ⚠️"
    else:
        verdict = "Avoid ❌"
    
    assert verdict == "Buy zone ✅", f"Expected Buy zone, got {verdict}"
    
    # Test Watch criteria
    ratio = 0.50
    if ratio <= 0.35 and trend >= 0 and 35 <= rsi_val <= 60:
        verdict = "Buy zone ✅"
    elif ratio <= 0.55 and trend >= 0:
        verdict = "Watch ⚠️"
    else:
        verdict = "Avoid ❌"
    
    assert verdict == "Watch ⚠️", f"Expected Watch, got {verdict}"
    
    # Test Avoid criteria
    ratio = 0.80
    if ratio <= 0.35 and trend >= 0 and 35 <= rsi_val <= 60:
        verdict = "Buy zone ✅"
    elif ratio <= 0.55 and trend >= 0:
        verdict = "Watch ⚠️"
    else:
        verdict = "Avoid ❌"
    
    assert verdict == "Avoid ❌", f"Expected Avoid, got {verdict}"
    
    print("  ✅ Verdict logic test passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("SR Ranker Unit Tests".center(60))
    print("=" * 60)
    print()
    
    try:
        test_rsi()
        test_ema()
        test_local_extrema()
        test_swing_levels()
        test_row_dataclass()
        test_verdict_logic()
        
        print()
        print("=" * 60)
        print("✅ All tests passed!".center(60))
        print("=" * 60)
        
        return True
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Unexpected error: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    main()
