# Btock Dashboard Usage Guide

## 🚀 Quick Start

### Main KPI Scoring Dashboard
The main application (`app.py`) provides the original KPI scoring functionality:

```bash
streamlit run app.py
```

**Features:**
- ✅ Upload Excel/CSV files with tickers
- ✅ Manual ticker entry
- ✅ Custom weight configuration for 5 categories
- ✅ Technical indicator analysis (11+ indicators)
- ✅ BUY/HOLD/SELL signals
- ✅ Excel export with formatting
- ✅ Database persistence

### Additional Sentiment Analysis Tool
For social media sentiment analysis, run the separate tool:

```bash
streamlit run sentiment_app.py
```

**Features:**
- ✅ X (Twitter) sentiment via Grok API
- ✅ Reddit analysis across multiple subreddits
- ✅ StockTwits public API integration
- ✅ Raw count methodology (+1/-1/0)
- ✅ Configurable time ranges
- ✅ Excel/CSV export

## 🔄 Recommended Workflow

### Option 1: KPI Analysis Only
1. Open the main dashboard: `streamlit run app.py`
2. Upload your ticker list or enter manually
3. Configure category weights
4. Run analysis and get BUY/HOLD/SELL signals
5. Export results

### Option 2: Combined Analysis
1. **Step 1**: Run KPI analysis in main dashboard
2. **Step 2**: Note your top 10 performing tickers
3. **Step 3**: Open sentiment tool: `streamlit run sentiment_app.py`
4. **Step 4**: Enter the top tickers for sentiment analysis
5. **Step 5**: Get comprehensive technical + sentiment insights

## 🚀 Deployment

### Railway Deployment
The main KPI dashboard deploys automatically to Railway:
- **Main URL**: https://btock-production.up.railway.app/
- **Procfile**: Configured to run `app.py` (original KPI dashboard)

### Environment Variables
```bash
# Database (Optional)
DATABASE_URL=postgresql://user:password@host:port/database

# For Sentiment Analysis (Optional)
XAI_API_KEY=your_grok_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

## 📁 File Structure

```
Btock/
├── app.py                    # 🎯 MAIN KPI Dashboard (Original)
├── sentiment_app.py          # 📊 Additional Sentiment Tool
├── kpi_app.py               # 📈 Alternative KPI version
├── modules/
│   ├── sentiment_analyzer.py # 🆕 Sentiment analysis engine
│   └── [other modules]       # Original KPI modules
└── requirements.txt          # All dependencies
```

## ✅ What's Preserved

The original KPI dashboard (`app.py`) maintains **100% of original functionality**:
- ✅ File upload (Excel/CSV)
- ✅ Manual ticker entry
- ✅ Weight sliders for all 5 categories
- ✅ All 11+ technical indicators
- ✅ BUY/HOLD/SELL signal generation
- ✅ Results table with sorting
- ✅ Excel export with conditional formatting
- ✅ Database persistence
- ✅ Progress tracking
- ✅ Error handling

## 🆕 What's Added

The sentiment analysis tool (`sentiment_app.py`) provides **additional functionality**:
- 🆕 Social media sentiment analysis
- 🆕 X (Twitter), Reddit, StockTwits integration
- 🆕 Raw count methodology
- 🆕 Configurable time ranges
- 🆕 Sentiment export capabilities

**No existing functionality was removed or modified.**
