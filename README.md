# 📊 Stock KPI Scoring Dashboard

A web-based dashboard for evaluating stocks daily using multiple KPIs (RSI, MACD, ADX, ATR, Moving Averages, CCI, Stochastic, Williams %R, ROC, Ultimate Oscillator, and Pivot Points).  
The app ranks tickers with a weighted scoring system and outputs **BUY / HOLD / SELL** signals.  

Built with **Streamlit**, deployable on **Railway**.

---

## 🚀 Features
- Upload an **Excel or CSV** with a list of tickers (up to 250+).
- Enter **custom weights** for:
  - Momentum  
  - Trend  
  - Volatility  
  - Strength  
  - Support/Resistance  
- Run analysis and view results in a live interactive table.
- Download results as an **Excel file** with scores and signals.
- Simple to deploy on **Railway** or run locally.

---

## 📦 Requirements
- Python 3.9+
- Libraries:
  - `streamlit`
  - `yfinance`
  - `pandas`
  - `pandas_ta`
  - `numpy`
  - `openpyxl`

Install dependencies:
```bash
pip install -r requirements.txt
