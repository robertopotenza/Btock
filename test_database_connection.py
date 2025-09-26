"""
Test script to verify database connection for Railway deployment
"""

import os
import psycopg2
from datetime import datetime

def test_database_connection():
    """Test the database connection and basic operations"""
    
    # Correct connection string (no space after railway)
    database_url = "postgresql://postgres:LKCCrHKOKWyckhyBOyNnhFycKNTvEgIn@trolley.proxy.rlwy.net:59937/railway"
    
    print("🧪 Testing Database Connection for Railway Deployment")
    print("=" * 60)
    
    try:
        # Test connection
        print("1. Testing database connection...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get database info
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"   ✅ Connected to: {version[0][:50]}...")
        
        # Check if tables exist
        print("\n2. Checking database schema...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('analysis_sessions', 'ticker_results', 'indicator_data')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        if len(tables) == 3:
            print("   ✅ All required tables exist:")
            for table in tables:
                print(f"      - {table[0]}")
        else:
            print(f"   ⚠️  Only {len(tables)} of 3 tables found")
        
        # Test a simple insert/select operation
        print("\n3. Testing database operations...")
        test_session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Insert test session
        cursor.execute("""
            INSERT INTO analysis_sessions (session_id, weights, total_tickers, status)
            VALUES (%s, %s, %s, %s)
        """, (test_session_id, '{"test": 1.0}', 1, 'test'))
        
        # Read it back
        cursor.execute("""
            SELECT session_id, status FROM analysis_sessions 
            WHERE session_id = %s
        """, (test_session_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Database operations working: {result[0]} - {result[1]}")
        
        # Clean up test data
        cursor.execute("DELETE FROM analysis_sessions WHERE session_id = %s", (test_session_id,))
        
        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Database connection test PASSED!")
        print("✅ Railway deployment should work with this connection string:")
        print(f"   DATABASE_URL={database_url}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database connection test FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    exit(0 if success else 1)
