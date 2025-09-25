# Enhanced Data Extraction Instructions

## Comprehensive Technical Analysis Data Extraction

The enhanced prompt should instruct the Grok agent to extract the following comprehensive set of technical indicators from each investing.com technical analysis page:

### 1. Summary Indicators
Extract the overall summary counts and recommendations for both Technical Indicators and Moving Averages sections, including the total number of buy, neutral, and sell signals.

### 2. Oscillators (with values and actions)
The agent should extract specific values and action recommendations for key oscillator indicators that measure momentum and overbought/oversold conditions:

- **RSI (14-period)**: Relative Strength Index value and corresponding buy/sell/neutral action
- **Stochastic (9,6)**: Stochastic oscillator value and action recommendation  
- **StochRSI (14-period)**: Stochastic RSI value and action signal
- **Williams %R**: Williams Percent Range value and action
- **ROC**: Rate of Change indicator value and action
- **Ultimate Oscillator**: Ultimate oscillator value and action recommendation

### 3. Trend-Following Indicators (with values and actions)
Extract trend-following indicators that help identify market direction and momentum:

- **MACD (12,26)**: Moving Average Convergence Divergence value and action
- **Bull/Bear Power (13-period)**: Elder's Bull/Bear Power value and action
- **ADX (14-period)**: Average Directional Index value and action
- **CCI (14-period)**: Commodity Channel Index value and action

### 4. Volatility and Other Indicators (with values and actions)
Extract volatility measures and additional technical indicators:

- **ATR (14-period)**: Average True Range value and action
- **Highs/Lows (14-period)**: High/Low indicator value and action

### 5. Detailed Moving Averages (values and actions for all periods)
Extract both Simple and Exponential Moving Averages for all available periods:

**Periods to extract**: 5, 10, 20, 50, 100, 200
**For each period, extract**:
- Simple Moving Average value and action (Buy/Sell/Neutral)
- Exponential Moving Average value and action (Buy/Sell/Neutral)

### 6. Complete Pivot Points (all five calculation methods)
Extract all support and resistance levels for each pivot point calculation method:

**Classic Pivot Points**: S3, S2, S1, Pivot Point, R1, R2, R3
**Fibonacci Pivot Points**: S3, S2, S1, Pivot Point, R1, R2, R3  
**Camarilla Pivot Points**: S3, S2, S1, Pivot Point, R1, R2, R3
**Woodie's Pivot Points**: S3, S2, S1, Pivot Point, R1, R2, R3
**DeMark's Pivot Points**: S1, Pivot Point, R1 (only three levels available)

### 7. Data Quality Requirements
The extraction instructions should emphasize:

- **Precision**: Extract exact numerical values as displayed
- **Completeness**: Capture both values and action recommendations where available
- **Error Handling**: Mark missing or unavailable data as "N/A"
- **Consistency**: Use standardized format for all extracted data
- **Validation**: Focus only on technical analysis sections, ignore news, charts, or unrelated content

### 8. Output Structure
The extracted data should be structured as a JSON object with clear categorization for easy processing into the final Markdown table format. Each category should contain both the raw values and the corresponding action recommendations to provide comprehensive technical analysis information.
