"""
Technical Indicators Module for Btock Stock KPI Scoring Dashboard
Calculates all required technical indicators using pandas_ta
"""

import pandas as pd
import ta
import numpy as np
from typing import Dict, Optional
import streamlit as st


class TechnicalIndicators:
    """Calculates technical indicators for stock analysis"""
    
    def __init__(self):
        self.indicators = {}
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate all technical indicators for the given stock data
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary with all calculated indicators
        """
        if data.empty or len(data) < 200:  # Need sufficient data for calculations
            return {}
        
        indicators = {}
        
        try:
            # Calculate momentum indicators
            momentum_indicators = self._calculate_momentum_indicators(data)
            indicators.update(momentum_indicators)
            
            # Calculate trend indicators
            trend_indicators = self._calculate_trend_indicators(data)
            indicators.update(trend_indicators)
            
            # Calculate volatility indicators
            volatility_indicators = self._calculate_volatility_indicators(data)
            indicators.update(volatility_indicators)
            
            # Calculate strength indicators
            strength_indicators = self._calculate_strength_indicators(data)
            indicators.update(strength_indicators)
            
            # Calculate support/resistance indicators
            support_resistance_indicators = self._calculate_support_resistance_indicators(data)
            indicators.update(support_resistance_indicators)
            
        except Exception as e:
            st.error(f"Error calculating indicators: {str(e)}")
            return {}
        
        return indicators
    
    def _calculate_momentum_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate momentum-based indicators"""
        indicators = {}
        
        try:
            # RSI (Relative Strength Index)
            rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
            indicators['rsi'] = float(rsi.iloc[-1]) if not rsi.empty else 50.0
            
            # Stochastic Oscillator
            stoch_k = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close']).stoch()
            stoch_d = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close']).stoch_signal()
            indicators['stoch_k'] = float(stoch_k.iloc[-1]) if not stoch_k.empty else 50.0
            indicators['stoch_d'] = float(stoch_d.iloc[-1]) if not stoch_d.empty else 50.0
            
            # Stochastic RSI (approximation using RSI)
            rsi_values = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
            if not rsi_values.empty:
                stoch_rsi_k = ta.momentum.StochasticOscillator(rsi_values, rsi_values, rsi_values).stoch()
                stoch_rsi_d = ta.momentum.StochasticOscillator(rsi_values, rsi_values, rsi_values).stoch_signal()
                indicators['stoch_rsi_k'] = float(stoch_rsi_k.iloc[-1]) if not stoch_rsi_k.empty else 50.0
                indicators['stoch_rsi_d'] = float(stoch_rsi_d.iloc[-1]) if not stoch_rsi_d.empty else 50.0
            else:
                indicators['stoch_rsi_k'] = 50.0
                indicators['stoch_rsi_d'] = 50.0
            
            # Williams %R
            willr = ta.momentum.WilliamsRIndicator(data['High'], data['Low'], data['Close']).williams_r()
            indicators['williams_r'] = float(willr.iloc[-1]) if not willr.empty else -50.0
            
            # Rate of Change (ROC)
            roc = ta.momentum.ROCIndicator(data['Close'], window=12).roc()
            indicators['roc'] = float(roc.iloc[-1]) if not roc.empty else 0.0
            
            # Ultimate Oscillator
            uo = ta.momentum.UltimateOscillator(data['High'], data['Low'], data['Close']).ultimate_oscillator()
            indicators['ultimate_oscillator'] = float(uo.iloc[-1]) if not uo.empty else 50.0
            
        except Exception as e:
            st.warning(f"Error calculating momentum indicators: {str(e)}")
            # Set default values
            indicators.update({
                'rsi': 50.0,
                'stoch_k': 50.0,
                'stoch_d': 50.0,
                'stoch_rsi_k': 50.0,
                'stoch_rsi_d': 50.0,
                'williams_r': -50.0,
                'roc': 0.0,
                'ultimate_oscillator': 50.0
            })
        
        return indicators
    
    def _calculate_trend_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate trend-based indicators"""
        indicators = {}
        
        try:
            # MACD
            macd_indicator = ta.trend.MACD(data['Close'])
            macd_line = macd_indicator.macd()
            macd_signal = macd_indicator.macd_signal()
            macd_histogram = macd_indicator.macd_diff()
            
            indicators['macd'] = float(macd_line.iloc[-1]) if not macd_line.empty else 0.0
            indicators['macd_signal'] = float(macd_signal.iloc[-1]) if not macd_signal.empty else 0.0
            indicators['macd_histogram'] = float(macd_histogram.iloc[-1]) if not macd_histogram.empty else 0.0
            
            # Moving Averages
            ma5 = ta.trend.SMAIndicator(data['Close'], window=5).sma_indicator()
            ma10 = ta.trend.SMAIndicator(data['Close'], window=10).sma_indicator()
            ma20 = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            ma50 = ta.trend.SMAIndicator(data['Close'], window=50).sma_indicator()
            ma200 = ta.trend.SMAIndicator(data['Close'], window=200).sma_indicator()
            
            current_price = float(data['Close'].iloc[-1])
            
            indicators['ma5'] = float(ma5.iloc[-1]) if not ma5.empty else current_price
            indicators['ma10'] = float(ma10.iloc[-1]) if not ma10.empty else current_price
            indicators['ma20'] = float(ma20.iloc[-1]) if not ma20.empty else current_price
            indicators['ma50'] = float(ma50.iloc[-1]) if not ma50.empty else current_price
            indicators['ma200'] = float(ma200.iloc[-1]) if not ma200.empty else current_price
            
            # Price relative to moving averages
            indicators['price_vs_ma5'] = (current_price - indicators['ma5']) / indicators['ma5'] * 100
            indicators['price_vs_ma20'] = (current_price - indicators['ma20']) / indicators['ma20'] * 100
            indicators['price_vs_ma50'] = (current_price - indicators['ma50']) / indicators['ma50'] * 100
            indicators['price_vs_ma200'] = (current_price - indicators['ma200']) / indicators['ma200'] * 100
            
            # Bull/Bear Power (Elder's Force Index approximation)
            ema13 = ta.trend.EMAIndicator(data['Close'], window=13).ema_indicator()
            if not ema13.empty:
                indicators['bull_power'] = float(data['High'].iloc[-1] - ema13.iloc[-1])
                indicators['bear_power'] = float(data['Low'].iloc[-1] - ema13.iloc[-1])
            else:
                indicators['bull_power'] = 0.0
                indicators['bear_power'] = 0.0
            
        except Exception as e:
            st.warning(f"Error calculating trend indicators: {str(e)}")
            current_price = float(data['Close'].iloc[-1])
            indicators.update({
                'macd': 0.0,
                'macd_signal': 0.0,
                'macd_histogram': 0.0,
                'ma5': current_price,
                'ma10': current_price,
                'ma20': current_price,
                'ma50': current_price,
                'ma200': current_price,
                'price_vs_ma5': 0.0,
                'price_vs_ma20': 0.0,
                'price_vs_ma50': 0.0,
                'price_vs_ma200': 0.0,
                'bull_power': 0.0,
                'bear_power': 0.0
            })
        
        return indicators
    
    def _calculate_volatility_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate volatility-based indicators"""
        indicators = {}
        
        try:
            # Average True Range (ATR)
            atr = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close'], window=14).average_true_range()
            indicators['atr'] = float(atr.iloc[-1]) if not atr.empty else 0.0
            
            # ATR as percentage of price
            current_price = float(data['Close'].iloc[-1])
            indicators['atr_percent'] = (indicators['atr'] / current_price) * 100 if current_price > 0 else 0.0
            
            # High/Low analysis (volatility measure)
            high_low_range = data['High'] - data['Low']
            indicators['avg_high_low_range'] = float(high_low_range.tail(14).mean())
            indicators['current_high_low_range'] = float(high_low_range.iloc[-1])
            
            # Price position within daily range
            daily_range = data['High'].iloc[-1] - data['Low'].iloc[-1]
            if daily_range > 0:
                indicators['price_position_in_range'] = (current_price - data['Low'].iloc[-1]) / daily_range
            else:
                indicators['price_position_in_range'] = 0.5
            
            # Volatility ratio (current vs average)
            if indicators['avg_high_low_range'] > 0:
                indicators['volatility_ratio'] = indicators['current_high_low_range'] / indicators['avg_high_low_range']
            else:
                indicators['volatility_ratio'] = 1.0
            
        except Exception as e:
            st.warning(f"Error calculating volatility indicators: {str(e)}")
            indicators.update({
                'atr': 0.0,
                'atr_percent': 0.0,
                'avg_high_low_range': 0.0,
                'current_high_low_range': 0.0,
                'price_position_in_range': 0.5,
                'volatility_ratio': 1.0
            })
        
        return indicators
    
    def _calculate_strength_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate strength-based indicators"""
        indicators = {}
        
        try:
            # Average Directional Index (ADX)
            adx_indicator = ta.trend.ADXIndicator(data['High'], data['Low'], data['Close'], window=14)
            adx_value = adx_indicator.adx()
            di_plus = adx_indicator.adx_pos()
            di_minus = adx_indicator.adx_neg()
            
            indicators['adx'] = float(adx_value.iloc[-1]) if not adx_value.empty else 25.0
            indicators['di_plus'] = float(di_plus.iloc[-1]) if not di_plus.empty else 25.0
            indicators['di_minus'] = float(di_minus.iloc[-1]) if not di_minus.empty else 25.0
            
            # Commodity Channel Index (CCI)
            cci = ta.trend.CCIIndicator(data['High'], data['Low'], data['Close'], window=20).cci()
            indicators['cci'] = float(cci.iloc[-1]) if not cci.empty else 0.0
            
            # Directional strength
            if indicators['di_plus'] + indicators['di_minus'] > 0:
                indicators['directional_strength'] = abs(indicators['di_plus'] - indicators['di_minus']) / (indicators['di_plus'] + indicators['di_minus'])
            else:
                indicators['directional_strength'] = 0.0
            
        except Exception as e:
            st.warning(f"Error calculating strength indicators: {str(e)}")
            indicators.update({
                'adx': 25.0,
                'di_plus': 25.0,
                'di_minus': 25.0,
                'cci': 0.0,
                'directional_strength': 0.0
            })
        
        return indicators
    
    def _calculate_support_resistance_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate support/resistance indicators (Pivot Points)"""
        indicators = {}
        
        try:
            # Get the last complete trading day data
            high = float(data['High'].iloc[-1])
            low = float(data['Low'].iloc[-1])
            close = float(data['Close'].iloc[-1])
            current_price = close
            
            # Classic Pivot Points
            pivot_classic = (high + low + close) / 3
            r1_classic = 2 * pivot_classic - low
            s1_classic = 2 * pivot_classic - high
            r2_classic = pivot_classic + (high - low)
            s2_classic = pivot_classic - (high - low)
            
            indicators['pivot_classic'] = pivot_classic
            indicators['r1_classic'] = r1_classic
            indicators['s1_classic'] = s1_classic
            indicators['r2_classic'] = r2_classic
            indicators['s2_classic'] = s2_classic
            
            # Fibonacci Pivot Points
            pivot_fib = pivot_classic
            r1_fib = pivot_fib + 0.382 * (high - low)
            s1_fib = pivot_fib - 0.382 * (high - low)
            r2_fib = pivot_fib + 0.618 * (high - low)
            s2_fib = pivot_fib - 0.618 * (high - low)
            
            indicators['pivot_fibonacci'] = pivot_fib
            indicators['r1_fibonacci'] = r1_fib
            indicators['s1_fibonacci'] = s1_fib
            indicators['r2_fibonacci'] = r2_fib
            indicators['s2_fibonacci'] = s2_fib
            
            # Camarilla Pivot Points
            r1_camarilla = close + 1.1 * (high - low) / 12
            s1_camarilla = close - 1.1 * (high - low) / 12
            r2_camarilla = close + 1.1 * (high - low) / 6
            s2_camarilla = close - 1.1 * (high - low) / 6
            
            indicators['r1_camarilla'] = r1_camarilla
            indicators['s1_camarilla'] = s1_camarilla
            indicators['r2_camarilla'] = r2_camarilla
            indicators['s2_camarilla'] = s2_camarilla
            
            # Woodie Pivot Points
            pivot_woodie = (high + low + 2 * close) / 4
            r1_woodie = 2 * pivot_woodie - low
            s1_woodie = 2 * pivot_woodie - high
            
            indicators['pivot_woodie'] = pivot_woodie
            indicators['r1_woodie'] = r1_woodie
            indicators['s1_woodie'] = s1_woodie
            
            # DeMark Pivot Points
            if close < data['Open'].iloc[-1]:
                x = high + 2 * low + close
            elif close > data['Open'].iloc[-1]:
                x = 2 * high + low + close
            else:
                x = high + low + 2 * close
            
            pivot_demark = x / 4
            r1_demark = x / 2 - low
            s1_demark = x / 2 - high
            
            indicators['pivot_demark'] = pivot_demark
            indicators['r1_demark'] = r1_demark
            indicators['s1_demark'] = s1_demark
            
            # Calculate price position relative to pivot levels
            # Classic pivot position
            if current_price > pivot_classic:
                if current_price > r1_classic:
                    indicators['pivot_position_classic'] = 1.0  # Above R1
                else:
                    indicators['pivot_position_classic'] = 0.5  # Between Pivot and R1
            else:
                if current_price < s1_classic:
                    indicators['pivot_position_classic'] = -1.0  # Below S1
                else:
                    indicators['pivot_position_classic'] = -0.5  # Between S1 and Pivot
            
            # Distance from nearest pivot level (normalized)
            pivot_distances = [
                abs(current_price - pivot_classic),
                abs(current_price - r1_classic),
                abs(current_price - s1_classic),
                abs(current_price - r2_classic),
                abs(current_price - s2_classic)
            ]
            min_distance = min(pivot_distances)
            indicators['nearest_pivot_distance'] = min_distance / current_price if current_price > 0 else 0.0
            
        except Exception as e:
            st.warning(f"Error calculating support/resistance indicators: {str(e)}")
            current_price = float(data['Close'].iloc[-1])
            indicators.update({
                'pivot_classic': current_price,
                'r1_classic': current_price * 1.01,
                's1_classic': current_price * 0.99,
                'r2_classic': current_price * 1.02,
                's2_classic': current_price * 0.98,
                'pivot_fibonacci': current_price,
                'r1_fibonacci': current_price * 1.01,
                's1_fibonacci': current_price * 0.99,
                'r2_fibonacci': current_price * 1.02,
                's2_fibonacci': current_price * 0.98,
                'r1_camarilla': current_price * 1.005,
                's1_camarilla': current_price * 0.995,
                'r2_camarilla': current_price * 1.01,
                's2_camarilla': current_price * 0.99,
                'pivot_woodie': current_price,
                'r1_woodie': current_price * 1.01,
                's1_woodie': current_price * 0.99,
                'pivot_demark': current_price,
                'r1_demark': current_price * 1.01,
                's1_demark': current_price * 0.99,
                'pivot_position_classic': 0.0,
                'nearest_pivot_distance': 0.01
            })
        
        return indicators
