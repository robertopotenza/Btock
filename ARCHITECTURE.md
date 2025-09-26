# Btock Application Architecture

## Overview
The Btock Stock KPI Scoring Dashboard is a Streamlit-based web application that provides daily stock evaluation using technical indicators and a weighted scoring system.

## Application Structure

```
btock/
├── app.py                 # Main Streamlit application
├── modules/
│   ├── __init__.py
│   ├── data_fetcher.py    # Yahoo Finance data retrieval
│   ├── indicators.py     # Technical indicator calculations
│   ├── scoring.py        # Scoring and normalization logic
│   └── utils.py          # Utility functions
├── requirements.txt      # Python dependencies
├── Procfile             # Railway deployment configuration
├── runtime.txt          # Python version specification
└── README.md            # Documentation
```

## Core Components

### 1. Data Layer (`data_fetcher.py`)
- **Purpose**: Fetch historical stock data from Yahoo Finance
- **Functions**:
  - `fetch_stock_data(ticker, period='1y')`: Get OHLCV data
  - `validate_ticker(ticker)`: Check if ticker exists
  - `batch_fetch_data(tickers)`: Fetch data for multiple tickers

### 2. Technical Indicators (`indicators.py`)
- **Purpose**: Calculate all required technical indicators
- **Categories**:
  - **Momentum**: RSI, Stochastic, StochRSI, Williams %R, ROC, Ultimate Oscillator
  - **Trend**: MACD, Moving Averages (5, 10, 20, 50, 200), Bull/Bear Power
  - **Volatility**: ATR, High/Low analysis
  - **Strength**: ADX, CCI
  - **Support/Resistance**: Pivot Points (Classic, Fibonacci, Camarilla, Woodie, DeMark)

### 3. Scoring Engine (`scoring.py`)
- **Purpose**: Normalize indicators and calculate weighted scores
- **Functions**:
  - `normalize_indicator(value, indicator_type)`: Normalize to -1 to +1 range
  - `calculate_category_scores(indicators)`: Calculate category averages
  - `calculate_final_score(category_scores, weights)`: Apply weights
  - `generate_signal(final_score)`: BUY/HOLD/SELL decision

### 4. Main Application (`app.py`)
- **Purpose**: Streamlit UI and workflow orchestration
- **Features**:
  - File upload (Excel/CSV)
  - Weight configuration interface
  - Progress tracking for large datasets
  - Interactive results table
  - Excel download functionality

## Database Schema (PostgreSQL)

### Tables

#### 1. `analysis_sessions`
```sql
CREATE TABLE analysis_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    weights JSONB NOT NULL,
    total_tickers INTEGER,
    status VARCHAR(20) DEFAULT 'pending'
);
```

#### 2. `ticker_results`
```sql
CREATE TABLE ticker_results (
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
```

#### 3. `indicator_data`
```sql
CREATE TABLE indicator_data (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES analysis_sessions(session_id),
    ticker VARCHAR(10) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    indicator_value DECIMAL(10,6),
    normalized_value DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Data Flow

1. **Input**: User uploads Excel/CSV with tickers and sets weights
2. **Validation**: Check ticker format and weight normalization
3. **Data Fetching**: Retrieve historical data from Yahoo Finance
4. **Indicator Calculation**: Compute all technical indicators
5. **Scoring**: Normalize indicators and calculate weighted scores
6. **Storage**: Save results to PostgreSQL database
7. **Display**: Show interactive table with sortable results
8. **Export**: Generate downloadable Excel file

## Deployment Configuration

### Railway Deployment
- **Procfile**: `web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- **Environment Variables**:
  - `DATABASE_URL`: PostgreSQL connection string
  - `PORT`: Railway-assigned port
- **Build Process**: Automatic via requirements.txt

### Performance Considerations
- **Caching**: Implement Streamlit caching for data fetching
- **Batch Processing**: Process tickers in batches to avoid timeouts
- **Progress Tracking**: Real-time progress updates for large datasets
- **Error Handling**: Graceful handling of invalid tickers and API failures

## Security & Best Practices
- **Input Validation**: Sanitize uploaded files and user inputs
- **Rate Limiting**: Respect Yahoo Finance API limits
- **Error Logging**: Comprehensive error tracking and logging
- **Data Privacy**: No sensitive financial data storage beyond session scope
