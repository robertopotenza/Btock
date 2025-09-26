"""
Scoring Module for Btock Stock KPI Scoring Dashboard
Handles indicator normalization and weighted scoring calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import streamlit as st


class ScoringEngine:
    """Handles indicator normalization and scoring calculations"""
    
    def __init__(self):
        self.category_weights = {
            'momentum': 0.2,
            'trend': 0.3,
            'volatility': 0.15,
            'strength': 0.2,
            'support_resistance': 0.15
        }
        
        # Thresholds for BUY/HOLD/SELL signals
        self.buy_threshold = 0.5
        self.sell_threshold = -0.5
    
    def normalize_indicator(self, value: float, indicator_name: str) -> float:
        """
        Normalize indicator value to -1 to +1 range
        
        Args:
            value: Raw indicator value
            indicator_name: Name of the indicator
            
        Returns:
            Normalized value between -1 and +1
        """
        try:
            # RSI-based indicators (0-100 range)
            if indicator_name in ['rsi', 'stoch_k', 'stoch_d', 'stoch_rsi_k', 'stoch_rsi_d', 'ultimate_oscillator']:
                # RSI: 70+ overbought (+1), 30- oversold (-1), 50 neutral (0)
                if value >= 70:
                    return min(1.0, (value - 70) / 30)
                elif value <= 30:
                    return max(-1.0, (value - 30) / 30)
                else:
                    return (value - 50) / 20
            
            # Williams %R (-100 to 0 range)
            elif indicator_name == 'williams_r':
                # -20+ overbought (+1), -80- oversold (-1)
                if value >= -20:
                    return min(1.0, (value + 20) / 20)
                elif value <= -80:
                    return max(-1.0, (value + 80) / 20)
                else:
                    return (value + 50) / 30
            
            # ROC (Rate of Change) - percentage
            elif indicator_name == 'roc':
                # Normalize around ±10% as extreme values
                return max(-1.0, min(1.0, value / 10))
            
            # MACD indicators
            elif indicator_name in ['macd', 'macd_signal', 'macd_histogram']:
                # Normalize based on typical MACD ranges (varies by stock)
                # Use a dynamic approach based on absolute value
                abs_value = abs(value)
                if abs_value == 0:
                    return 0.0
                # Scale to reasonable range, with larger values approaching ±1
                normalized = value / (abs_value + 1)
                return max(-1.0, min(1.0, normalized))
            
            # Price vs Moving Average percentages
            elif indicator_name.startswith('price_vs_ma'):
                # ±5% as moderate, ±10% as strong signals
                return max(-1.0, min(1.0, value / 10))
            
            # Bull/Bear Power
            elif indicator_name in ['bull_power', 'bear_power']:
                # Normalize based on typical ranges (varies by stock price)
                if value == 0:
                    return 0.0
                # Use logarithmic scaling for better distribution
                sign = 1 if value > 0 else -1
                abs_value = abs(value)
                normalized = sign * min(1.0, np.log10(abs_value + 1) / 2)
                return normalized
            
            # ATR and volatility indicators
            elif indicator_name in ['atr', 'atr_percent', 'avg_high_low_range', 'current_high_low_range']:
                # Higher volatility = higher positive score (up to a point)
                if value <= 0:
                    return -1.0
                # Normalize with logarithmic scaling
                normalized = min(1.0, np.log10(value + 1) / 2)
                return normalized
            
            # Volatility ratio
            elif indicator_name == 'volatility_ratio':
                # 1.0 = normal volatility (0), >2.0 = high volatility (+1), <0.5 = low volatility (-1)
                if value >= 2.0:
                    return 1.0
                elif value <= 0.5:
                    return -1.0
                else:
                    return (value - 1.0)
            
            # Price position in range
            elif indicator_name == 'price_position_in_range':
                # 0.0 = at low (-1), 1.0 = at high (+1), 0.5 = middle (0)
                return (value - 0.5) * 2
            
            # ADX and strength indicators
            elif indicator_name in ['adx', 'di_plus', 'di_minus']:
                # ADX: 25+ strong trend (+1), <20 weak trend (-1)
                if indicator_name == 'adx':
                    if value >= 25:
                        return min(1.0, (value - 25) / 25)
                    else:
                        return max(-1.0, (value - 20) / 20)
                else:  # DI+ and DI-
                    # Higher values indicate stronger directional movement
                    return min(1.0, (value - 25) / 25)
            
            # CCI (Commodity Channel Index)
            elif indicator_name == 'cci':
                # ±100 as moderate levels, ±200 as extreme
                return max(-1.0, min(1.0, value / 200))
            
            # Directional strength
            elif indicator_name == 'directional_strength':
                # 0.0 = no direction (0), 1.0 = strong direction (+1)
                return value * 2 - 1
            
            # Pivot point position
            elif indicator_name == 'pivot_position_classic':
                # Already normalized to -1, -0.5, 0.5, 1.0 range
                return value
            
            # Nearest pivot distance
            elif indicator_name == 'nearest_pivot_distance':
                # Closer to pivot = higher score (support/resistance strength)
                # Invert the distance so closer = higher score
                if value <= 0:
                    return 1.0
                # Use exponential decay for distance
                return max(-1.0, 1.0 - value * 100)
            
            # Default normalization for unknown indicators
            else:
                # Use z-score like normalization with clipping
                if value == 0:
                    return 0.0
                # Simple scaling approach
                abs_value = abs(value)
                sign = 1 if value > 0 else -1
                normalized = sign * min(1.0, abs_value / (abs_value + 1))
                return normalized
                
        except Exception as e:
            st.warning(f"Error normalizing {indicator_name}: {str(e)}")
            return 0.0
    
    def calculate_category_scores(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate category scores from normalized indicators
        
        Args:
            indicators: Dictionary of raw indicator values
            
        Returns:
            Dictionary with category scores
        """
        category_scores = {}
        
        try:
            # Momentum indicators
            momentum_indicators = [
                'rsi', 'stoch_k', 'stoch_d', 'stoch_rsi_k', 'stoch_rsi_d',
                'williams_r', 'roc', 'ultimate_oscillator'
            ]
            momentum_values = []
            for indicator in momentum_indicators:
                if indicator in indicators:
                    normalized = self.normalize_indicator(indicators[indicator], indicator)
                    momentum_values.append(normalized)
            
            category_scores['momentum'] = np.mean(momentum_values) if momentum_values else 0.0
            
            # Trend indicators
            trend_indicators = [
                'macd', 'macd_histogram', 'price_vs_ma5', 'price_vs_ma20',
                'price_vs_ma50', 'price_vs_ma200', 'bull_power', 'bear_power'
            ]
            trend_values = []
            for indicator in trend_indicators:
                if indicator in indicators:
                    normalized = self.normalize_indicator(indicators[indicator], indicator)
                    trend_values.append(normalized)
            
            category_scores['trend'] = np.mean(trend_values) if trend_values else 0.0
            
            # Volatility indicators
            volatility_indicators = [
                'atr_percent', 'volatility_ratio', 'price_position_in_range'
            ]
            volatility_values = []
            for indicator in volatility_indicators:
                if indicator in indicators:
                    normalized = self.normalize_indicator(indicators[indicator], indicator)
                    volatility_values.append(normalized)
            
            category_scores['volatility'] = np.mean(volatility_values) if volatility_values else 0.0
            
            # Strength indicators
            strength_indicators = [
                'adx', 'cci', 'directional_strength'
            ]
            strength_values = []
            for indicator in strength_indicators:
                if indicator in indicators:
                    normalized = self.normalize_indicator(indicators[indicator], indicator)
                    strength_values.append(normalized)
            
            category_scores['strength'] = np.mean(strength_values) if strength_values else 0.0
            
            # Support/Resistance indicators
            support_resistance_indicators = [
                'pivot_position_classic', 'nearest_pivot_distance'
            ]
            support_resistance_values = []
            for indicator in support_resistance_indicators:
                if indicator in indicators:
                    normalized = self.normalize_indicator(indicators[indicator], indicator)
                    support_resistance_values.append(normalized)
            
            category_scores['support_resistance'] = np.mean(support_resistance_values) if support_resistance_values else 0.0
            
        except Exception as e:
            st.error(f"Error calculating category scores: {str(e)}")
            category_scores = {
                'momentum': 0.0,
                'trend': 0.0,
                'volatility': 0.0,
                'strength': 0.0,
                'support_resistance': 0.0
            }
        
        return category_scores
    
    def calculate_final_score(self, category_scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calculate final weighted score
        
        Args:
            category_scores: Dictionary with category scores
            weights: Dictionary with category weights
            
        Returns:
            Final weighted score between -1 and +1
        """
        try:
            # Ensure weights sum to 1.0
            total_weight = sum(weights.values())
            if total_weight == 0:
                return 0.0
            
            # Normalize weights if they don't sum to 1.0
            if abs(total_weight - 1.0) > 0.001:
                weights = {k: v / total_weight for k, v in weights.items()}
            
            # Calculate weighted score
            final_score = 0.0
            for category, score in category_scores.items():
                if category in weights:
                    final_score += score * weights[category]
            
            # Ensure score is within bounds
            return max(-1.0, min(1.0, final_score))
            
        except Exception as e:
            st.error(f"Error calculating final score: {str(e)}")
            return 0.0
    
    def generate_signal(self, final_score: float) -> str:
        """
        Generate BUY/HOLD/SELL signal based on final score
        
        Args:
            final_score: Final weighted score
            
        Returns:
            Signal string: 'BUY', 'HOLD', or 'SELL'
        """
        if final_score >= self.buy_threshold:
            return 'BUY'
        elif final_score <= self.sell_threshold:
            return 'SELL'
        else:
            return 'HOLD'
    
    def set_thresholds(self, buy_threshold: float, sell_threshold: float):
        """
        Set custom thresholds for signal generation
        
        Args:
            buy_threshold: Threshold for BUY signal
            sell_threshold: Threshold for SELL signal
        """
        self.buy_threshold = max(-1.0, min(1.0, buy_threshold))
        self.sell_threshold = max(-1.0, min(1.0, sell_threshold))
        
        # Ensure sell threshold is less than buy threshold
        if self.sell_threshold >= self.buy_threshold:
            self.sell_threshold = self.buy_threshold - 0.1
    
    def analyze_ticker(self, indicators: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
        """
        Complete analysis for a single ticker
        
        Args:
            indicators: Dictionary of raw indicator values
            weights: Dictionary of category weights
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Calculate category scores
            category_scores = self.calculate_category_scores(indicators)
            
            # Calculate final weighted score
            final_score = self.calculate_final_score(category_scores, weights)
            
            # Generate signal
            signal = self.generate_signal(final_score)
            
            # Prepare results
            results = {
                'momentum_score': round(category_scores['momentum'], 4),
                'trend_score': round(category_scores['trend'], 4),
                'volatility_score': round(category_scores['volatility'], 4),
                'strength_score': round(category_scores['strength'], 4),
                'support_resistance_score': round(category_scores['support_resistance'], 4),
                'final_weighted_score': round(final_score, 4),
                'signal': signal
            }
            
            return results
            
        except Exception as e:
            st.error(f"Error analyzing ticker: {str(e)}")
            return {
                'momentum_score': 0.0,
                'trend_score': 0.0,
                'volatility_score': 0.0,
                'strength_score': 0.0,
                'support_resistance_score': 0.0,
                'final_weighted_score': 0.0,
                'signal': 'HOLD'
            }
