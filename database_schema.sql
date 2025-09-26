-- Btock Normalization Database Schema
-- This schema creates tables to store raw KPI data and normalized values

-- Main KPI data table to store raw technical analysis data
CREATE TABLE IF NOT EXISTS kpi_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255),
    fetch_date DATE NOT NULL,
    fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Summary Data
    ti_summary VARCHAR(20),
    ti_buy_count INTEGER,
    ti_neutral_count INTEGER,
    ti_sell_count INTEGER,
    ma_summary VARCHAR(20),
    ma_buy_count INTEGER,
    ma_sell_count INTEGER,
    
    -- Oscillators (Raw Values)
    rsi_value DECIMAL(10,4),
    rsi_action VARCHAR(20),
    stochastic_value DECIMAL(10,4),
    stochastic_action VARCHAR(20),
    stochrsi_value DECIMAL(10,4),
    stochrsi_action VARCHAR(20),
    williams_r_value DECIMAL(10,4),
    williams_r_action VARCHAR(20),
    roc_value DECIMAL(10,4),
    roc_action VARCHAR(20),
    ultimate_oscillator_value DECIMAL(10,4),
    ultimate_oscillator_action VARCHAR(20),
    
    -- Trend Indicators (Raw Values)
    macd_value DECIMAL(10,4),
    macd_action VARCHAR(20),
    macd_signal DECIMAL(10,4),
    adx_value DECIMAL(10,4),
    adx_action VARCHAR(20),
    cci_value DECIMAL(10,4),
    cci_action VARCHAR(20),
    bull_bear_power_value DECIMAL(10,4),
    bull_bear_power_action VARCHAR(20),
    
    -- Volatility Indicators (Raw Values)
    atr_value DECIMAL(10,4),
    atr_action VARCHAR(20),
    highs_lows_value DECIMAL(10,4),
    highs_lows_action VARCHAR(20),
    
    -- Moving Averages (Raw Values)
    ma5_simple_value DECIMAL(10,4),
    ma5_simple_action VARCHAR(20),
    ma5_exp_value DECIMAL(10,4),
    ma5_exp_action VARCHAR(20),
    ma10_simple_value DECIMAL(10,4),
    ma10_simple_action VARCHAR(20),
    ma10_exp_value DECIMAL(10,4),
    ma10_exp_action VARCHAR(20),
    ma20_simple_value DECIMAL(10,4),
    ma20_simple_action VARCHAR(20),
    ma20_exp_value DECIMAL(10,4),
    ma20_exp_action VARCHAR(20),
    ma50_simple_value DECIMAL(10,4),
    ma50_simple_action VARCHAR(20),
    ma50_exp_value DECIMAL(10,4),
    ma50_exp_action VARCHAR(20),
    ma100_simple_value DECIMAL(10,4),
    ma100_simple_action VARCHAR(20),
    ma100_exp_value DECIMAL(10,4),
    ma100_exp_action VARCHAR(20),
    ma200_simple_value DECIMAL(10,4),
    ma200_simple_action VARCHAR(20),
    ma200_exp_value DECIMAL(10,4),
    ma200_exp_action VARCHAR(20),

    -- Pivot Points (Raw Values)
    classic_s3 DECIMAL(10,4),
    classic_s2 DECIMAL(10,4),
    classic_s1 DECIMAL(10,4),
    classic_pivot DECIMAL(10,4),
    classic_r1 DECIMAL(10,4),
    classic_r2 DECIMAL(10,4),
    classic_r3 DECIMAL(10,4),
    fibonacci_s3 DECIMAL(10,4),
    fibonacci_s2 DECIMAL(10,4),
    fibonacci_s1 DECIMAL(10,4),
    fibonacci_pivot DECIMAL(10,4),
    fibonacci_r1 DECIMAL(10,4),
    fibonacci_r2 DECIMAL(10,4),
    fibonacci_r3 DECIMAL(10,4),
    camarilla_s3 DECIMAL(10,4),
    camarilla_s2 DECIMAL(10,4),
    camarilla_s1 DECIMAL(10,4),
    camarilla_pivot DECIMAL(10,4),
    camarilla_r1 DECIMAL(10,4),
    camarilla_r2 DECIMAL(10,4),
    camarilla_r3 DECIMAL(10,4),
    woodie_s3 DECIMAL(10,4),
    woodie_s2 DECIMAL(10,4),
    woodie_s1 DECIMAL(10,4),
    woodie_pivot DECIMAL(10,4),
    woodie_r1 DECIMAL(10,4),
    woodie_r2 DECIMAL(10,4),
    woodie_r3 DECIMAL(10,4),
    demark_s1 DECIMAL(10,4),
    demark_pivot DECIMAL(10,4),
    demark_r1 DECIMAL(10,4),
    
    -- Current Price (needed for normalization calculations)
    current_price DECIMAL(10,4),
    high_14 DECIMAL(10,4),
    low_14 DECIMAL(10,4),
    
    -- Indexes for performance
    UNIQUE(ticker, fetch_date, fetch_time)
);

-- Normalization table to store calculated normalized values
CREATE TABLE IF NOT EXISTS normalization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kpi_data_id INTEGER NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    fetch_date DATE NOT NULL,
    fetch_time TIMESTAMP NOT NULL,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Momentum Normalized Values (range typically -1 to 1)
    rsi_normalized DECIMAL(10,6),
    stochastic_normalized DECIMAL(10,6),
    stochrsi_normalized DECIMAL(10,6),
    williams_r_normalized DECIMAL(10,6),
    roc_normalized DECIMAL(10,6),
    ultimate_oscillator_normalized DECIMAL(10,6),
    
    -- Trend Normalized Values
    macd_normalized DECIMAL(10,6),
    ma_trend_5_10_normalized DECIMAL(10,6),   -- MA5 vs MA10
    ma_trend_10_20_normalized DECIMAL(10,6),  -- MA10 vs MA20
    ma_trend_20_50_normalized DECIMAL(10,6),  -- MA20 vs MA50
    ma_trend_50_100_normalized DECIMAL(10,6), -- MA50 vs MA100
    ma_trend_100_200_normalized DECIMAL(10,6),-- MA100 vs MA200
    ma_trend_20_200_normalized DECIMAL(10,6), -- MA20 vs MA200 (legacy support)
    ma_trend_50_200_normalized DECIMAL(10,6), -- MA50 vs MA200 (legacy support)
    bull_bear_power_normalized DECIMAL(10,6),

    -- Volatility Normalized Values
    atr_normalized DECIMAL(10,6),
    highs_lows_normalized DECIMAL(10,6),
    
    -- Strength Normalized Values
    adx_normalized DECIMAL(10,6),
    cci_normalized DECIMAL(10,6),
    
    -- Support/Resistance Normalized Values
    pivot_classic_normalized DECIMAL(10,6),
    pivot_fibonacci_normalized DECIMAL(10,6),
    pivot_camarilla_normalized DECIMAL(10,6),
    pivot_woodie_normalized DECIMAL(10,6),
    pivot_demark_normalized DECIMAL(10,6),
    
    -- Composite Scores (calculated from multiple indicators)
    momentum_score DECIMAL(10,6),      -- Average of momentum indicators
    trend_score DECIMAL(10,6),         -- Average of trend indicators
    volatility_score DECIMAL(10,6),    -- Average of volatility indicators
    strength_score DECIMAL(10,6),      -- Average of strength indicators
    support_resistance_score DECIMAL(10,6), -- Average of pivot indicators
    overall_score DECIMAL(10,6),       -- Weighted average of all categories
    
    -- Foreign key constraint
    FOREIGN KEY (kpi_data_id) REFERENCES kpi_data(id) ON DELETE CASCADE,
    
    -- Unique constraint
    UNIQUE(kpi_data_id)
);

-- View for easy access to combined raw and normalized data
DROP VIEW IF EXISTS kpi_with_normalization;
CREATE VIEW IF NOT EXISTS kpi_with_normalization AS
SELECT 
    k.*,
    n.rsi_normalized,
    n.stochastic_normalized,
    n.stochrsi_normalized,
    n.williams_r_normalized,
    n.roc_normalized,
    n.ultimate_oscillator_normalized,
    n.macd_normalized,
    n.ma_trend_5_10_normalized,
    n.ma_trend_10_20_normalized,
    n.ma_trend_20_50_normalized,
    n.ma_trend_20_200_normalized,
    n.ma_trend_50_100_normalized,
    n.ma_trend_100_200_normalized,
    n.ma_trend_50_200_normalized,
    n.bull_bear_power_normalized,
    n.atr_normalized,
    n.highs_lows_normalized,
    n.adx_normalized,
    n.cci_normalized,
    n.pivot_classic_normalized,
    n.pivot_fibonacci_normalized,
    n.pivot_camarilla_normalized,
    n.pivot_woodie_normalized,
    n.pivot_demark_normalized,
    n.momentum_score,
    n.trend_score,
    n.volatility_score,
    n.strength_score,
    n.support_resistance_score,
    n.overall_score,
    n.calculation_time
FROM kpi_data k
LEFT JOIN normalization n ON k.id = n.kpi_data_id;

-- Composite score table based on extended weighting formula
CREATE TABLE IF NOT EXISTS ticker_composite_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    normalization_id INTEGER NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    fetch_date DATE NOT NULL,
    fetch_time TIMESTAMP NOT NULL,
    momentum_component DECIMAL(10,6),
    trend_component DECIMAL(10,6),
    volatility_component DECIMAL(10,6),
    strength_component DECIMAL(10,6),
    support_resistance_component DECIMAL(10,6),
    composite_score DECIMAL(10,6),
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (normalization_id) REFERENCES normalization(id) ON DELETE CASCADE,
    UNIQUE(normalization_id)
);



-- Sample queries for testing
-- SELECT * FROM kpi_with_normalization WHERE ticker = 'AAPL' ORDER BY fetch_time DESC LIMIT 1;
-- SELECT ticker, overall_score FROM normalization ORDER BY overall_score DESC LIMIT 10;


-- Create indexes after tables are created
CREATE INDEX IF NOT EXISTS idx_kpi_data_ticker_date ON kpi_data(ticker, fetch_date);
CREATE INDEX IF NOT EXISTS idx_kpi_data_fetch_time ON kpi_data(fetch_time);
CREATE INDEX IF NOT EXISTS idx_normalization_ticker_date ON normalization(ticker, fetch_date);
CREATE INDEX IF NOT EXISTS idx_normalization_kpi_data ON normalization(kpi_data_id);
CREATE INDEX IF NOT EXISTS idx_normalization_scores ON normalization(overall_score, momentum_score, trend_score);
