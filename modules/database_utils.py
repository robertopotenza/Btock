"""
Database Utility Functions for Btock Stock KPI Scoring Dashboard
Handles database operations and data type conversions
"""

import numpy as np
import pandas as pd
import psycopg2
import json
from typing import Any, Dict, List, Optional
import streamlit as st


class DatabaseUtils:
    """Utility functions for database operations"""
    
    @staticmethod
    def convert_numpy_types(data: Any) -> Any:
        """
        Convert numpy types to Python native types for database compatibility
        
        Args:
            data: Data that may contain numpy types
            
        Returns:
            Data with numpy types converted to Python native types
        """
        if data is None:
            return None
        
        # Handle numpy arrays first (before checking for item() method)
        if isinstance(data, np.ndarray):
            return data.tolist()
        
        # Handle numpy types
        if isinstance(data, (np.integer, np.int64, np.int32)):
            return int(data)
        elif isinstance(data, (np.floating, np.float64, np.float32)):
            return float(data)
        elif isinstance(data, np.bool_):
            return bool(data)
        
        # Handle numpy scalars (single values with item() method)
        elif hasattr(data, 'item') and hasattr(data, 'dtype'):
            try:
                return data.item()
            except ValueError:
                # If item() fails, try converting based on dtype
                if np.issubdtype(data.dtype, np.integer):
                    return int(data)
                elif np.issubdtype(data.dtype, np.floating):
                    return float(data)
                else:
                    return str(data)
        
        # Handle dictionaries recursively
        elif isinstance(data, dict):
            return {key: DatabaseUtils.convert_numpy_types(value) for key, value in data.items()}
        
        # Handle lists recursively
        elif isinstance(data, list):
            return [DatabaseUtils.convert_numpy_types(item) for item in data]
        
        # Return as-is for other types
        return data
    
    @staticmethod
    def prepare_result_for_database(result: Dict) -> Dict:
        """
        Prepare a result dictionary for database insertion by converting numpy types
        
        Args:
            result: Result dictionary from analysis
            
        Returns:
            Result dictionary with converted types
        """
        try:
            # Create a copy to avoid modifying the original
            prepared_result = result.copy()
            
            # Convert all values
            for key, value in prepared_result.items():
                prepared_result[key] = DatabaseUtils.convert_numpy_types(value)
            
            return prepared_result
            
        except Exception as e:
            st.error(f"Error preparing result for database: {str(e)}")
            return result
    
    @staticmethod
    def safe_database_insert(cursor, query: str, params: tuple) -> bool:
        """
        Safely execute a database insert with proper error handling
        
        Args:
            cursor: Database cursor
            query: SQL query string
            params: Query parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert all parameters to ensure database compatibility
            safe_params = tuple(DatabaseUtils.convert_numpy_types(param) for param in params)
            
            cursor.execute(query, safe_params)
            return True
            
        except Exception as e:
            st.error(f"Database insert error: {str(e)}")
            return False
    
    @staticmethod
    def validate_database_connection(database_url: str) -> bool:
        """
        Validate database connection
        
        Args:
            database_url: Database connection string
            
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Database connection validation failed: {str(e)}")
            return False


class DataTypeConverter:
    """Handles conversion between different data types for database operations"""
    
    @staticmethod
    def pandas_to_database(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert pandas DataFrame for database insertion
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with converted types
        """
        try:
            # Create a copy
            converted_df = df.copy()
            
            # Convert numpy types in each column
            for column in converted_df.columns:
                converted_df[column] = converted_df[column].apply(
                    lambda x: DatabaseUtils.convert_numpy_types(x)
                )
            
            return converted_df
            
        except Exception as e:
            st.error(f"Error converting DataFrame: {str(e)}")
            return df
    
    @staticmethod
    def json_serializable(obj: Any) -> Any:
        """
        Make an object JSON serializable by converting numpy types
        
        Args:
            obj: Object to convert
            
        Returns:
            JSON serializable object
        """
        try:
            return DatabaseUtils.convert_numpy_types(obj)
        except Exception as e:
            st.error(f"Error making object JSON serializable: {str(e)}")
            return str(obj)  # Fallback to string representation
