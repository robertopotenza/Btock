# 📊 Stock KPI Scoring Dashboard

A web-based dashboard for evaluating stocks daily using multiple KPIs (RSI, MACD, ADX, ATR, Moving Averages, CCI, Stochastic, Williams %R, ROC, Ultimate Oscillator, and Pivot Points).  
The app ranks tickers with a weighted scoring system and outputs **BUY / HOLD / SELL** signals and a global score per ticker.

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

📊 How the Scoring Works

For each ticker, the system calculates scores across five key categories:

Momentum → captures short-term signals (overbought/oversold).

Trend → measures the direction of the stock’s movement.

Volatility → tracks how strongly the price is moving day to day.

Strength → evaluates the reliability of the current trend.

Support/Resistance → positions the price relative to pivot levels.

Each category produces a normalized score, and the user assigns weights to reflect its importance. These are then combined into a Final Weighted Score per ticker.

The Final Score allows you to rank and compare multiple stocks daily, making it easy to filter which tickers are potential BUY, HOLD, or SELL candidates.

---
How the Scoring Normalization Works
flowchart TD
  A[Input: OHLCV Data + KPIs] --> B1[Momentum KPIs<br/>RSI, Stoch, StochRSI,<br/>Williams %R, ROC, Ultimate Osc]
  A --> B2[Trend KPIs<br/>MACD, MA5–200, Bull/Bear Power]
  A --> B3[Volatility KPIs<br/>ATR, Highs/Lows]
  A --> B4[Strength KPIs<br/>ADX, CCI]
  A --> B5[Support/Resistance KPIs<br/>Pivot Points: Classic, Fib, Camarilla, Woodie, DeMark]

  B1 --> C1[Normalize to -1..+1]
  B2 --> C2[Normalize to -1..+1]
  B3 --> C3[Normalize to -1..+1]
  B4 --> C4[Normalize to -1..+1]
  B5 --> C5[Normalize to -1..+1]

  C1 --> D1[Momentum Score = avg(norm KPIs)]
  C2 --> D2[Trend Score = avg(norm KPIs)]
  C3 --> D3[Volatility Score = avg(norm KPIs)]
  C4 --> D4[Strength Score = avg(norm KPIs)]
  C5 --> D5[Support/Resistance Score = avg(norm KPIs)]

  subgraph Weights (User-defined; must sum to 1.0)
    W1[Momentum wM]:::w
    W2[Trend wT]:::w
    W3[Volatility wV]:::w
    W4[Strength wS]:::w
    W5[Support/Res wP]:::w
  end
  classDef w fill:#eef,stroke:#88f;

  D1 --> E1[(wM × Momentum)]
  D2 --> E2[(wT × Trend)]
  D3 --> E3[(wV × Volatility)]
  D4 --> E4[(wS × Strength)]
  D5 --> E5[(wP × Support/Res)]

  E1 --> F[Final Weighted Score<br/>= Σ (w × Category Score)]
  E2 --> F
  E3 --> F
  E4 --> F
  E5 --> F

  F --> G{Thresholds}
  G --> H1[BUY if Score > +0.5]
  G --> H2[HOLD if -0.5 ≤ Score ≤ +0.5]
  G --> H3[SELL if Score < -0.5]
----

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
