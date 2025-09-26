"""
Database Setup Script for Btock Stock KPI Scoring Dashboard
Creates the required PostgreSQL tables
"""

import psycopg2
import os
import sys

def create_database_schema(database_url: str):
    """Create the database schema"""
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Connected to database successfully!")
        
        # Create analysis_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                weights JSONB NOT NULL,
                total_tickers INTEGER,
                status VARCHAR(20) DEFAULT 'pending'
            );
        """)
        
        print("Created analysis_sessions table")
        
        # Create ticker_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticker_results (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(50) REFERENCES analysis_sessions(session_id),
                ticker VARCHAR(10) NOT NULL,
                current_price DECIMAL(10,2),
                momentum_score DECIMAL(5,4),
                trend_score DECIMAL(5,4),
                volatility_score DECIMAL(5,4),
                strength_score DECIMAL(5,4),
                support_resistance_score DECIMAL(5,4),
                final_weighted_score DECIMAL(5,4),
                signal VARCHAR(4) CHECK (signal IN ('BUY', 'HOLD', 'SELL')),
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("Created ticker_results table")
        
        # Create indicator_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicator_data (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(50) REFERENCES analysis_sessions(session_id),
                ticker VARCHAR(10) NOT NULL,
                indicator_name VARCHAR(50) NOT NULL,
                indicator_value DECIMAL(10,6),
                normalized_value DECIMAL(5,4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("Created indicator_data table")
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticker_results_session_id 
            ON ticker_results(session_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticker_results_ticker 
            ON ticker_results(ticker);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_indicator_data_session_id 
            ON indicator_data(session_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_indicator_data_ticker 
            ON indicator_data(ticker);
        """)
        
        print("Created database indexes")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database schema created successfully!")
        
    except Exception as e:
        print(f"Error creating database schema: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Get database URL from environment or command line
    database_url = os.getenv('DATABASE_URL')
    
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
    
    if not database_url:
        print("Please provide DATABASE_URL as environment variable or command line argument")
        print("Usage: python setup_database.py [DATABASE_URL]")
        sys.exit(1)
    
    create_database_schema(database_url)
