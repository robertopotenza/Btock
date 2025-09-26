"""
Utility Functions for Btock Stock KPI Scoring Dashboard
Helper functions for file processing, data validation, and export
"""

import pandas as pd
import streamlit as st
import io
from typing import List, Dict, Optional, Tuple
import re
import uuid
from datetime import datetime


class FileProcessor:
    """Handles file upload and processing operations"""
    
    @staticmethod
    def process_uploaded_file(uploaded_file) -> Optional[List[str]]:
        """
        Process uploaded Excel or CSV file to extract ticker list
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            List of ticker symbols or None if error
        """
        try:
            if uploaded_file is None:
                return None
            
            # Determine file type and read accordingly
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload CSV or Excel files.")
                return None
            
            # Look for ticker column (case insensitive)
            ticker_column = None
            for col in df.columns:
                if col.lower() in ['ticker', 'symbol', 'stock', 'tickers', 'symbols']:
                    ticker_column = col
                    break
            
            if ticker_column is None:
                st.error("No 'Ticker' column found in the uploaded file. Please ensure your file has a column named 'Ticker'.")
                return None
            
            # Extract tickers and clean them
            tickers = df[ticker_column].dropna().astype(str).tolist()
            cleaned_tickers = []
            
            for ticker in tickers:
                # Clean ticker symbol
                cleaned_ticker = FileProcessor.clean_ticker_symbol(ticker)
                if cleaned_ticker:
                    cleaned_tickers.append(cleaned_ticker)
            
            if not cleaned_tickers:
                st.error("No valid ticker symbols found in the uploaded file.")
                return None
            
            # Remove duplicates while preserving order
            unique_tickers = list(dict.fromkeys(cleaned_tickers))
            
            st.success(f"Successfully loaded {len(unique_tickers)} unique ticker symbols.")
            
            return unique_tickers
            
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
            return None
    
    @staticmethod
    def clean_ticker_symbol(ticker: str) -> Optional[str]:
        """
        Clean and validate ticker symbol
        
        Args:
            ticker: Raw ticker symbol
            
        Returns:
            Cleaned ticker symbol or None if invalid
        """
        if not ticker or pd.isna(ticker):
            return None
        
        # Convert to string and strip whitespace
        ticker = str(ticker).strip().upper()
        
        # Remove common prefixes/suffixes and special characters
        ticker = re.sub(r'[^A-Z0-9.-]', '', ticker)
        
        # Basic validation - ticker should be 1-5 characters for most exchanges
        if len(ticker) < 1 or len(ticker) > 10:
            return None
        
        # Skip obviously invalid entries
        invalid_patterns = ['N/A', 'NULL', 'NONE', 'ERROR', '']
        if ticker in invalid_patterns:
            return None
        
        return ticker
    
    @staticmethod
    def create_results_excel(results_df: pd.DataFrame) -> bytes:
        """
        Create Excel file from results DataFrame
        
        Args:
            results_df: DataFrame with analysis results
            
        Returns:
            Excel file as bytes
        """
        try:
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Write main results
                results_df.to_excel(writer, sheet_name='Stock Analysis Results', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Stock Analysis Results']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Add formatting for signal column
                from openpyxl.styles import PatternFill
                
                # Find signal column
                signal_col = None
                for idx, col in enumerate(results_df.columns, 1):
                    if col.lower() == 'signal':
                        signal_col = idx
                        break
                
                if signal_col:
                    # Color code signals
                    buy_fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')  # Light green
                    sell_fill = PatternFill(start_color='FFB6C1', end_color='FFB6C1', fill_type='solid')  # Light pink
                    hold_fill = PatternFill(start_color='FFFFE0', end_color='FFFFE0', fill_type='solid')  # Light yellow
                    
                    for row in range(2, len(results_df) + 2):  # Skip header row
                        cell = worksheet.cell(row=row, column=signal_col)
                        if cell.value == 'BUY':
                            cell.fill = buy_fill
                        elif cell.value == 'SELL':
                            cell.fill = sell_fill
                        elif cell.value == 'HOLD':
                            cell.fill = hold_fill
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            st.error(f"Error creating Excel file: {str(e)}")
            return b''


class WeightValidator:
    """Handles weight validation and normalization"""
    
    @staticmethod
    def validate_and_normalize_weights(weights: Dict[str, float]) -> Tuple[Dict[str, float], bool]:
        """
        Validate and normalize weights to sum to 1.0
        
        Args:
            weights: Dictionary of category weights
            
        Returns:
            Tuple of (normalized_weights, is_valid)
        """
        try:
            # Check if all weights are non-negative
            for category, weight in weights.items():
                if weight < 0:
                    st.error(f"Weight for {category} cannot be negative.")
                    return weights, False
            
            # Calculate total weight
            total_weight = sum(weights.values())
            
            if total_weight == 0:
                st.error("Total weight cannot be zero. Please assign positive weights.")
                return weights, False
            
            # Normalize weights to sum to 1.0
            normalized_weights = {k: v / total_weight for k, v in weights.items()}
            
            # Show normalization message if needed
            if abs(total_weight - 1.0) > 0.001:
                st.info(f"Weights normalized from total {total_weight:.3f} to 1.000")
            
            return normalized_weights, True
            
        except Exception as e:
            st.error(f"Error validating weights: {str(e)}")
            return weights, False
    
    @staticmethod
    def get_default_weights() -> Dict[str, float]:
        """Get default category weights"""
        return {
            'momentum': 0.2,
            'trend': 0.3,
            'volatility': 0.15,
            'strength': 0.2,
            'support_resistance': 0.15
        }


class SessionManager:
    """Manages analysis sessions and results"""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def create_session_summary(session_id: str, weights: Dict[str, float], 
                             total_tickers: int, successful_tickers: int) -> Dict:
        """
        Create session summary
        
        Args:
            session_id: Unique session identifier
            weights: Category weights used
            total_tickers: Total number of tickers processed
            successful_tickers: Number of successfully analyzed tickers
            
        Returns:
            Session summary dictionary
        """
        return {
            'session_id': session_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'weights': weights,
            'total_tickers': total_tickers,
            'successful_tickers': successful_tickers,
            'success_rate': (successful_tickers / total_tickers * 100) if total_tickers > 0 else 0
        }


class DataFormatter:
    """Handles data formatting and display"""
    
    @staticmethod
    def format_results_for_display(results: List[Dict]) -> pd.DataFrame:
        """
        Format analysis results for display in Streamlit
        
        Args:
            results: List of analysis result dictionaries
            
        Returns:
            Formatted DataFrame
        """
        try:
            if not results:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Reorder columns for better display
            column_order = [
                'ticker', 'current_price', 'final_weighted_score', 'signal',
                'momentum_score', 'trend_score', 'volatility_score', 
                'strength_score', 'support_resistance_score', 'error_message'
            ]
            
            # Only include columns that exist
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]
            
            # Format numeric columns
            numeric_columns = [
                'current_price', 'final_weighted_score', 'momentum_score',
                'trend_score', 'volatility_score', 'strength_score', 'support_resistance_score'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    if col == 'current_price':
                        df[col] = df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
                    else:
                        df[col] = df[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
            
            # Rename columns for display
            column_names = {
                'ticker': 'Ticker',
                'current_price': 'Current Price',
                'final_weighted_score': 'Final Score',
                'signal': 'Signal',
                'momentum_score': 'Momentum',
                'trend_score': 'Trend',
                'volatility_score': 'Volatility',
                'strength_score': 'Strength',
                'support_resistance_score': 'Support/Resistance',
                'error_message': 'Error'
            }
            
            df = df.rename(columns=column_names)
            
            # Sort by Final Score (descending)
            if 'Final Score' in df.columns:
                # Convert back to numeric for sorting
                df['Final Score Numeric'] = df['Final Score'].str.replace('N/A', '0').astype(float)
                df = df.sort_values('Final Score Numeric', ascending=False)
                df = df.drop('Final Score Numeric', axis=1)
            
            return df
            
        except Exception as e:
            st.error(f"Error formatting results: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def create_summary_stats(results: List[Dict]) -> Dict:
        """
        Create summary statistics from results
        
        Args:
            results: List of analysis result dictionaries
            
        Returns:
            Summary statistics dictionary
        """
        try:
            if not results:
                return {}
            
            # Filter out results with errors
            valid_results = [r for r in results if 'error_message' not in r or not r['error_message']]
            
            if not valid_results:
                return {'total_analyzed': len(results), 'successful': 0, 'errors': len(results)}
            
            # Calculate signal distribution
            signals = [r['signal'] for r in valid_results]
            signal_counts = {
                'BUY': signals.count('BUY'),
                'HOLD': signals.count('HOLD'),
                'SELL': signals.count('SELL')
            }
            
            # Calculate score statistics
            scores = [r['final_weighted_score'] for r in valid_results]
            
            summary = {
                'total_analyzed': len(results),
                'successful': len(valid_results),
                'errors': len(results) - len(valid_results),
                'signal_distribution': signal_counts,
                'score_stats': {
                    'mean': np.mean(scores),
                    'median': np.median(scores),
                    'std': np.std(scores),
                    'min': np.min(scores),
                    'max': np.max(scores)
                }
            }
            
            return summary
            
        except Exception as e:
            st.error(f"Error creating summary stats: {str(e)}")
            return {}
