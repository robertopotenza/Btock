# Btock Stock KPI Scoring Dashboard - Deployment Guide

## 🚀 Deployment Status

✅ **Application Development**: Complete  
✅ **Database Setup**: PostgreSQL schema created and tested  
✅ **GitHub Repository**: All files committed and pushed  
✅ **Local Testing**: Application runs successfully on Streamlit  
⚠️ **Railway Deployment**: Requires manual setup through Railway dashboard  

## 📋 Deployment Steps for Railway

### 1. Connect GitHub Repository to Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose the repository: `robertopotenza/Btock`
5. Railway will automatically detect the configuration files

### 2. Environment Variables

Set the following environment variable in Railway:

```
DATABASE_URL=postgresql://postgres:LKCCrHKOKWyckhyBOyNnhFycKNTvEgIn@trolley.proxy.rlwy.net:59937/railway
```

### 3. Deployment Configuration

The repository includes all necessary deployment files:

- **`Procfile`**: Defines the start command for Railway
- **`requirements.txt`**: Python dependencies
- **`runtime.txt`**: Python version specification
- **`railway.json`**: Railway-specific configuration
- **`nixpacks.toml`**: Build configuration

### 4. Custom Domain Setup

To deploy at `https://btock-production.up.railway.app/`:

1. In Railway dashboard, go to your project settings
2. Navigate to "Domains" section
3. Add custom domain: `btock-production.up.railway.app`
4. Configure DNS settings as instructed by Railway

## 🗄️ Database Information

**Database**: PostgreSQL on Railway  
**Connection String**: `postgresql://postgres:LKCCrHKOKWyckhyBOyNnhFycKNTvEgIn@trolley.proxy.rlwy.net:59937/railway`

**Tables Created**:
- `analysis_sessions`: Stores analysis session metadata
- `ticker_results`: Stores individual ticker analysis results
- `indicator_data`: Stores detailed indicator values

## 🧪 Testing

The application has been tested locally and all core functionality works:

- ✅ Data fetching from Yahoo Finance
- ✅ Technical indicator calculations (RSI, MACD, ADX, ATR, etc.)
- ✅ Scoring engine with weighted categories
- ✅ Database connectivity and schema
- ✅ File upload and processing
- ✅ Excel export functionality

## 📊 Application Features

### Core Functionality
- **File Upload**: Excel/CSV ticker lists
- **Weight Configuration**: 5 categories (Momentum, Trend, Volatility, Strength, Support/Resistance)
- **Technical Analysis**: 11+ indicators with normalization
- **Scoring System**: Weighted final scores with BUY/HOLD/SELL signals
- **Interactive Results**: Sortable table with real-time updates
- **Export**: Excel download with formatted results
- **Progress Tracking**: Real-time progress for large datasets (250+ tickers)

### Technical Indicators Included
- **Momentum**: RSI, Stochastic, Williams %R, ROC, Ultimate Oscillator
- **Trend**: MACD, Moving Averages (5,10,20,50,200), Bull/Bear Power
- **Volatility**: ATR, High/Low Analysis
- **Strength**: ADX, CCI, Directional Movement
- **Support/Resistance**: Pivot Points (Classic, Fibonacci, Camarilla, Woodie, DeMark)

## 🔧 Manual Deployment Alternative

If automatic deployment doesn't work, you can deploy manually using Railway CLI:

```bash
# Login to Railway
railway login

# Link to existing project or create new one
railway link

# Set environment variables
railway variables set DATABASE_URL="postgresql://postgres:LKCCrHKOKWyckhyBOyNnhFycKNTvEgIn@trolley.proxy.rlwy.net:59937/railway"

# Deploy
railway up
```

## 📞 Support

For deployment issues:
- Check Railway logs in the dashboard
- Verify environment variables are set correctly
- Ensure the GitHub repository is properly connected
- Contact Railway support if domain configuration issues persist

## 🎯 Expected Result

Once deployed, the application will be accessible at:
**https://btock-production.up.railway.app/**

The dashboard will provide:
- File upload interface for ticker lists
- Weight configuration sliders
- Real-time analysis with progress tracking
- Interactive results table with sorting
- Excel export functionality
- Summary statistics and signal distribution
