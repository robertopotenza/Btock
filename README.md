# Btock Stock Analysis Dashboard

A comprehensive web-based platform for stock analysis combining **technical indicators** and **social media sentiment** analysis.

## 🚀 Features

### 📈 KPI Scoring Dashboard
- **Technical Indicator Analysis** using 11+ indicators across 5 categories
- **Weighted Scoring System** with customizable category weights
- **BUY/HOLD/SELL Signals** based on comprehensive technical analysis
- **Excel Export** with professional formatting and conditional coloring
- **Database Persistence** for analysis history and session management

### 📊 Sentiment Scoring Dashboard
- **Social Media Sentiment Analysis** from multiple platforms
- **X (Twitter)** sentiment via Grok API integration
- **Reddit** analysis across relevant subreddits (stocks, wallstreetbets, investing)
- **StockTwits** public API for sentiment-tagged messages
- **Raw Count Methodology** (+1 bullish, -1 bearish, 0 neutral)
- **Configurable Time Ranges** (1 hour to 1 week lookback)

## 🔄 Workflow Options

### Option 1: KPI Scoring Only
1. Upload ticker list (Excel/CSV) or enter manually
2. Configure category weights (Momentum, Trend, Volatility, Strength, Support/Resistance)
3. Run technical analysis across all indicators
4. Get BUY/HOLD/SELL signals with detailed scoring
5. Export results to Excel or CSV

### Option 2: Sentiment Analysis Only
1. Enter tickers manually or upload file
2. Configure time range for analysis
3. Run sentiment analysis across social platforms
4. Get net sentiment scores and platform breakdowns
5. Export sentiment results

### Option 3: Combined Analysis (Recommended)
1. **Step 1**: Run KPI Scoring to rank all tickers by technical strength
2. **Step 2**: Extract top 10 performing tickers automatically
3. **Step 3**: Run Sentiment Analysis on top performers
4. **Step 4**: Get comprehensive technical + sentiment insights
5. **Step 5**: Make informed investment decisions

## 📊 Technical Indicators (KPI Scoring)

### Momentum Indicators
- **RSI** (Relative Strength Index)
- **Stochastic Oscillator**
- **Williams %R**
- **ROC** (Rate of Change)
- **Ultimate Oscillator**

### Trend Indicators
- **MACD** (Moving Average Convergence Divergence)
- **Moving Averages** (SMA, EMA)
- **Bull/Bear Power**

### Volatility Indicators
- **ATR** (Average True Range)
- **High/Low Analysis**

### Strength Indicators
- **ADX** (Average Directional Index)
- **CCI** (Commodity Channel Index)
- **Directional Movement**

### Support/Resistance Indicators
- **Pivot Points** (Classic, Fibonacci, Camarilla, Woodie, DeMark)

## 📱 Sentiment Data Sources

### X (Twitter) via Grok API
- Real-time tweet analysis with advanced NLP
- Excludes retweets for quality filtering
- Sentiment classification: positive/negative/neutral
- Configurable time range filtering

### Reddit Analysis
- Subreddit coverage: stocks, wallstreetbets, investing, SecurityAnalysis
- Keyword-based sentiment detection
- Post title and content analysis
- Bullish/bearish keyword matching

### StockTwits Public API
- Native sentiment tags from StockTwits platform
- Bullish/Bearish/Neutral classifications
- Real-time message stream analysis
- No API key required

## 🧮 Scoring Methodologies

### KPI Scoring (Technical Analysis)
- Each indicator normalized to **-1 to +1 scale**
- Category scores calculated as **weighted averages**
- Final score determines signal:
  - **BUY**: Score ≥ 0.5
  - **HOLD**: -0.5 < Score < 0.5
  - **SELL**: Score ≤ -0.5

### Sentiment Scoring (Social Media)
- **Raw count system** (not averages)
- Bullish/positive mention = **+1**
- Bearish/negative mention = **-1**
- Neutral mention = **0**
- **Net score** = Sum of all mentions
- **SentimentTotal** = Sum across all platforms

### Example Sentiment Output
```
Ticker   X    Reddit   StockTwits   SentimentTotal
AAPL     +2   +1       -1           +2
TSLA     +5   0        -2           +3
CRDO     +3   +1       -2           +2
```

## 🚀 Deployment

### Railway Platform (Recommended)
The application is configured for deployment on Railway with:
- **Dockerfile** for containerized deployment
- **railway.json** for deployment configuration
- **Procfile** for process management
- **Environment variables** for API keys and database

### Environment Variables Required
```bash
# Database (Optional)
DATABASE_URL=postgresql://user:password@host:port/database

# Sentiment Analysis APIs
XAI_API_KEY=your_grok_api_key
XAI_API_URL=https://api.x.ai/v1/chat/completions
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=Btock Sentiment Analyzer v1.0
```

### Deployment Options
1. **Main Dashboard**: `app.py` - Application hub with tool selection
2. **KPI Only**: `kpi_app.py` - Technical analysis dashboard
3. **Sentiment Only**: `sentiment_app.py` - Social sentiment analysis
4. **Combined**: Use main dashboard for integrated workflow

## 📁 Project Structure

```
Btock/
├── app.py                      # Main application hub
├── kpi_app.py                  # KPI scoring dashboard
├── sentiment_app.py            # Sentiment analysis dashboard
├── modules/
│   ├── data_fetcher.py         # Yahoo Finance integration
│   ├── indicators.py           # Technical indicator calculations
│   ├── scoring.py              # KPI scoring engine
│   ├── sentiment_analyzer.py   # Sentiment analysis engine
│   ├── utils.py                # Utility functions
│   └── database_utils.py       # Database operations
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── railway.json               # Railway deployment config
├── Procfile                   # Process configuration
└── README.md                  # This file
```

## 🔧 Installation & Setup

### Local Development
```bash
# Clone repository
git clone https://github.com/robertopotenza/Btock.git
cd Btock

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export DATABASE_URL="postgresql://..."
export XAI_API_KEY="your_key"
export REDDIT_CLIENT_ID="your_id"
export REDDIT_CLIENT_SECRET="your_secret"
export REDDIT_USER_AGENT="Btock Sentiment Analyzer v1.0"

# Optional: provide these only if you need authenticated Reddit access
# For 2FA accounts append the current code to the password (example: my-password:123456)
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password_or_app_password"

# Run application
streamlit run app.py
```

### Docker Deployment
```bash
# Build image
docker build -t btock-dashboard .

# Run container
docker run -p 8501:8501 \
  -e DATABASE_URL="postgresql://..." \
  -e XAI_API_KEY="your_key" \
  btock-dashboard
```

## 📊 Data Sources & APIs

- **Yahoo Finance**: Historical OHLCV data via `yfinance` library
- **Technical Indicators**: Calculated using `ta` library
- **X (Twitter)**: Grok API for advanced sentiment analysis
- **Reddit**: PRAW (Python Reddit API Wrapper)
- **StockTwits**: Public REST API (no authentication required)
- **Database**: PostgreSQL for session and result persistence

## 🎯 Use Cases

### Day Trading
- Quick technical analysis with real-time sentiment
- Focus on momentum and volatility indicators
- Short-term sentiment trends from social media

### Swing Trading
- Combined technical and sentiment analysis
- Medium-term trend identification
- Social media momentum confirmation

### Long-term Investing
- Fundamental technical strength via KPI scoring
- Long-term sentiment trend analysis
- Portfolio screening and ranking

### Risk Management
- Volatility analysis through ATR and price ranges
- Sentiment-based risk assessment
- Multi-timeframe analysis capabilities

## 🔮 Future Enhancements

- **News Sentiment**: Integration with financial news APIs
- **Options Flow**: Unusual options activity analysis
- **Crypto Support**: Cryptocurrency technical and sentiment analysis
- **Mobile App**: React Native mobile application
- **API Endpoints**: RESTful API for programmatic access
- **Machine Learning**: Predictive models using historical data
- **Real-time Alerts**: Push notifications for signal changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For questions, issues, or feature requests, please open an issue on GitHub or contact the development team.

---

**Btock Stock Analysis Dashboard** - Comprehensive Technical and Sentiment Analysis for Informed Investment Decisions
