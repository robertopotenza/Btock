# Investing.com Technical Analysis Data Structure

## Available Data Categories

### 1. Technical Indicators Summary
- **Overall Summary**: Strong Buy/Buy/Neutral/Sell/Strong Sell
- **Buy Count**: Number of indicators showing buy signal
- **Neutral Count**: Number of indicators showing neutral signal  
- **Sell Count**: Number of indicators showing sell signal

### 2. Individual Technical Indicators
**Oscillators:**
- RSI(14): Value + Action (Buy/Sell/Neutral)
- STOCH(9,6): Value + Action
- STOCHRSI(14): Value + Action  
- Williams %R: Value + Action
- ROC: Value + Action
- Ultimate Oscillator: Value + Action

**Trend-Following:**
- MACD(12,26): Value + Action
- Bull/Bear Power(13): Value + Action
- ADX(14): Value + Action
- CCI(14): Value + Action

**Volatility & Other:**
- ATR(14): Value + Action
- Highs/Lows(14): Value + Action

### 3. Moving Averages Summary
- **Overall Summary**: Strong Buy/Buy/Neutral/Sell/Strong Sell
- **Buy Count**: Number of MAs showing buy signal
- **Sell Count**: Number of MAs showing sell signal

### 4. Individual Moving Averages
**Available Periods:** 5, 10, 20, 50, 100, 200
**Types:**
- Simple Moving Average: Value + Action
- Exponential Moving Average: Value + Action

### 5. Pivot Points (All 5 Types)
**Classic Pivot Points:**
- S3, S2, S1, Pivot Point, R1, R2, R3

**Fibonacci Pivot Points:**
- S3, S2, S1, Pivot Point, R1, R2, R3

**Camarilla Pivot Points:**
- S3, S2, S1, Pivot Point, R1, R2, R3

**Woodie's Pivot Points:**
- S3, S2, S1, Pivot Point, R1, R2, R3

**DeMark's Pivot Points:**
- S1, Pivot Point, R1 (only 3 levels available)

## Data Format Examples
- RSI(14): 72.105 (Buy)
- MACD(12,26): 2.07 (Buy)
- MA5 Simple: 254.44 (Buy)
- MA50 Exponential: 248.65 (Buy)
- Classic Pivot: 254.98
- Fibonacci R1: 256.21

## Notes
- All indicators include both numerical values and action recommendations
- Pivot points provide multiple support/resistance levels
- Data is timestamped (e.g., "Sep 25, 2025 08:05PM GMT")
- Missing data should be marked as "N/A"
