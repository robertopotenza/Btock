/**
 * KPI Normalization Calculator
 * Implements the specified normalization formulas for all KPI categories
 */

class NormalizationCalculator {
  constructor() {
    // Default values for missing data
    this.defaults = {
      rsi: 50,
      stochastic: 50,
      stochrsi: 0.5,
      williamsR: -50,
      roc: 0,
      ultimateOscillator: 50,
      adx: 25,
      cci: 0
    };
  }

  /**
   * Parse numeric value from string, handling various formats
   */
  parseNumeric(value) {
    if (value === null || value === undefined || value === 'N/A' || value === '') {
      return null;
    }
    
    if (typeof value === 'number') {
      return value;
    }
    
    // Remove any non-numeric characters except decimal point and minus sign
    const cleaned = String(value).replace(/[^\d.-]/g, '');
    const parsed = parseFloat(cleaned);
    
    return isNaN(parsed) ? null : parsed;
  }

  /**
   * Safe division with null handling
   */
  safeDivide(numerator, denominator) {
    if (numerator === null || denominator === null || denominator === 0) {
      return null;
    }
    return numerator / denominator;
  }

  /**
   * Momentum Indicators Normalization
   */
  
  // RSI (14): (RSI - 50) / 50
  normalizeRSI(rsi) {
    const value = this.parseNumeric(rsi);
    if (value === null) return null;
    return (value - 50) / 50;
  }

  // Stochastic (9,6): (StochK - 50) / 50
  normalizeStochastic(stochastic) {
    const value = this.parseNumeric(stochastic);
    if (value === null) return null;
    return (value - 50) / 50;
  }

  // StochRSI (14): (StochRSI - 0.5) / 0.5
  normalizeStochRSI(stochRSI) {
    const value = this.parseNumeric(stochRSI);
    if (value === null) return null;
    return (value - 0.5) / 0.5;
  }

  // Williams %R: (WilliamsR + 50) / 50 // range -100 → 0
  normalizeWilliamsR(williamsR) {
    const value = this.parseNumeric(williamsR);
    if (value === null) return null;
    return (value + 50) / 50;
  }

  // ROC: ROC / 100
  normalizeROC(roc) {
    const value = this.parseNumeric(roc);
    if (value === null) return null;
    return value / 100;
  }

  // Ultimate Oscillator: (UltOsc - 50) / 50
  normalizeUltimateOscillator(ultimateOsc) {
    const value = this.parseNumeric(ultimateOsc);
    if (value === null) return null;
    return (value - 50) / 50;
  }

  /**
   * Trend Indicators Normalization
   */

  // MACD: (MACD - Signal) / ABS(Signal)
  normalizeMacd(macd, signal) {
    const macdValue = this.parseNumeric(macd);
    const signalValue = this.parseNumeric(signal);
    
    if (macdValue === null || signalValue === null || Math.abs(signalValue) === 0) {
      return null;
    }
    
    return (macdValue - signalValue) / Math.abs(signalValue);
  }

  // Moving Averages: (ShortMA - LongMA) / LongMA
  normalizeMovingAverageTrend(shortMA, longMA) {
    const short = this.parseNumeric(shortMA);
    const long = this.parseNumeric(longMA);
    
    if (short === null || long === null || long === 0) {
      return null;
    }
    
    return (short - long) / long;
  }

  // Bull/Bear Power (13): BullBear / ATR
  normalizeBullBearPower(bullBear, atr) {
    const bbValue = this.parseNumeric(bullBear);
    const atrValue = this.parseNumeric(atr);
    
    if (bbValue === null || atrValue === null || atrValue === 0) {
      return null;
    }
    
    return bbValue / atrValue;
  }

  /**
   * Volatility Indicators Normalization
   */

  // ATR (14): ATR / Close
  normalizeATR(atr, close) {
    const atrValue = this.parseNumeric(atr);
    const closeValue = this.parseNumeric(close);
    
    if (atrValue === null || closeValue === null || closeValue === 0) {
      return null;
    }
    
    return atrValue / closeValue;
  }

  // Highs/Lows (14): (Close - Low14) / (High14 - Low14)
  normalizeHighsLows(close, high14, low14) {
    const closeValue = this.parseNumeric(close);
    const highValue = this.parseNumeric(high14);
    const lowValue = this.parseNumeric(low14);
    
    if (closeValue === null || highValue === null || lowValue === null || (highValue - lowValue) === 0) {
      return null;
    }
    
    return (closeValue - lowValue) / (highValue - lowValue);
  }

  /**
   * Strength Indicators Normalization
   */

  // ADX (14): (ADX - 25) / 25
  normalizeADX(adx) {
    const value = this.parseNumeric(adx);
    if (value === null) return null;
    return (value - 25) / 25;
  }

  // CCI (14): CCI / 200
  normalizeCCI(cci) {
    const value = this.parseNumeric(cci);
    if (value === null) return null;
    return value / 200;
  }

  /**
   * Support/Resistance Indicators Normalization
   */

  // Generic pivot normalization helper
  normalizePivotGeneric(close, pivot, r1, s1) {
    const closeValue = this.parseNumeric(close);
    const pivotValue = this.parseNumeric(pivot);
    const r1Value = this.parseNumeric(r1);
    const s1Value = this.parseNumeric(s1);

    if (closeValue === null || pivotValue === null || r1Value === null || s1Value === null || (r1Value - s1Value) === 0) {
      return null;
    }

    return (closeValue - pivotValue) / (r1Value - s1Value);
  }

  // Pivot (Classic): (Close - Pivot) / (R1 - S1)
  normalizePivotClassic(close, pivot, r1, s1) {
    return this.normalizePivotGeneric(close, pivot, r1, s1);
  }

  // Pivot (Fibonacci): (Close - FibPivot) / (FibR1 - FibS1)
  normalizePivotFibonacci(close, fibPivot, fibR1, fibS1) {
    return this.normalizePivotGeneric(close, fibPivot, fibR1, fibS1);
  }

  // Pivot (Camarilla): (Close - CamPivot) / (CamR1 - CamS1)
  normalizePivotCamarilla(close, camPivot, camR1, camS1) {
    return this.normalizePivotGeneric(close, camPivot, camR1, camS1);
  }

  // Pivot (Woodie): (Close - WoodiePivot) / (WoodieR1 - WoodieS1)
  normalizePivotWoodie(close, woodiePivot, woodieR1, woodieS1) {
    return this.normalizePivotGeneric(close, woodiePivot, woodieR1, woodieS1);
  }

  // Pivot (DeMark): (Close - DeMarkPivot) / (DeMarkR1 - DeMarkS1)
  normalizePivotDeMark(close, demarkPivot, demarkR1, demarkS1) {
    return this.normalizePivotGeneric(close, demarkPivot, demarkR1, demarkS1);
  }

  /**
   * Composite Score Calculations
   */

  // Calculate average of non-null values
  calculateAverage(values) {
    const validValues = values.filter(v => v !== null && !isNaN(v));
    if (validValues.length === 0) return null;
    return validValues.reduce((sum, val) => sum + val, 0) / validValues.length;
  }

  // Calculate momentum score from momentum indicators
  calculateMomentumScore(rsi, stochastic, stochRSI, williamsR, roc, ultimateOsc) {
    const scores = [
      this.normalizeRSI(rsi),
      this.normalizeStochastic(stochastic),
      this.normalizeStochRSI(stochRSI),
      this.normalizeWilliamsR(williamsR),
      this.normalizeROC(roc),
      this.normalizeUltimateOscillator(ultimateOsc)
    ];
    return this.calculateAverage(scores);
  }

  // Calculate trend score from trend indicators
  calculateTrendScore(...trendValues) {
    return this.calculateAverage(trendValues);
  }

  // Calculate volatility score from volatility indicators
  calculateVolatilityScore(atrNorm, highsLowsNorm) {
    const scores = [atrNorm, highsLowsNorm];
    return this.calculateAverage(scores);
  }

  // Calculate strength score from strength indicators
  calculateStrengthScore(adxNorm, cciNorm) {
    const scores = [adxNorm, cciNorm];
    return this.calculateAverage(scores);
  }

  // Calculate support/resistance score from pivot indicators
  calculateSupportResistanceScore(...pivotValues) {
    return this.calculateAverage(pivotValues);
  }

  // Calculate overall score with weighted average
  calculateOverallScore(momentumScore, trendScore, volatilityScore, strengthScore, supportResistanceScore) {
    const weights = {
      momentum: 0.25,
      trend: 0.30,
      volatility: 0.15,
      strength: 0.20,
      supportResistance: 0.10
    };

    const weightedScores = [];
    
    if (momentumScore !== null) weightedScores.push(momentumScore * weights.momentum);
    if (trendScore !== null) weightedScores.push(trendScore * weights.trend);
    if (volatilityScore !== null) weightedScores.push(volatilityScore * weights.volatility);
    if (strengthScore !== null) weightedScores.push(strengthScore * weights.strength);
    if (supportResistanceScore !== null) weightedScores.push(supportResistanceScore * weights.supportResistance);

    if (weightedScores.length === 0) return null;
    
    return weightedScores.reduce((sum, score) => sum + score, 0);
  }

  /**
   * Main normalization function that processes all KPI data
   */
  normalizeKpiData(kpiData) {
    // Extract current price (assuming it's available in the data)
    const currentPrice = kpiData.current_price || kpiData.ma20_simple_value || kpiData.ma50_simple_value;

    // Momentum normalization
    const rsi_normalized = this.normalizeRSI(kpiData.rsi_value);
    const stochastic_normalized = this.normalizeStochastic(kpiData.stochastic_value);
    const stochrsi_normalized = this.normalizeStochRSI(kpiData.stochrsi_value);
    const williams_r_normalized = this.normalizeWilliamsR(kpiData.williams_r_value);
    const roc_normalized = this.normalizeROC(kpiData.roc_value);
    const ultimate_oscillator_normalized = this.normalizeUltimateOscillator(kpiData.ultimate_oscillator_value);

    // Trend normalization
    const macd_normalized = this.normalizeMacd(kpiData.macd_value, kpiData.macd_signal);
    const ma_trend_5_10_normalized = this.normalizeMovingAverageTrend(kpiData.ma5_simple_value, kpiData.ma10_simple_value);
    const ma_trend_10_20_normalized = this.normalizeMovingAverageTrend(kpiData.ma10_simple_value, kpiData.ma20_simple_value);
    const ma_trend_20_50_normalized = this.normalizeMovingAverageTrend(kpiData.ma20_simple_value, kpiData.ma50_simple_value);
    const ma_trend_50_100_normalized = this.normalizeMovingAverageTrend(kpiData.ma50_simple_value, kpiData.ma100_simple_value);
    const ma_trend_100_200_normalized = this.normalizeMovingAverageTrend(kpiData.ma100_simple_value, kpiData.ma200_simple_value);
    const ma_trend_20_200_normalized = this.normalizeMovingAverageTrend(kpiData.ma20_simple_value, kpiData.ma200_simple_value);
    const ma_trend_50_200_normalized = this.normalizeMovingAverageTrend(kpiData.ma50_simple_value, kpiData.ma200_simple_value);
    const bull_bear_power_normalized = this.normalizeBullBearPower(kpiData.bull_bear_power_value, kpiData.atr_value);

    // Volatility normalization
    const atr_normalized = this.normalizeATR(kpiData.atr_value, currentPrice);
    const highs_lows_normalized = this.normalizeHighsLows(currentPrice, kpiData.high_14, kpiData.low_14);

    // Strength normalization
    const adx_normalized = this.normalizeADX(kpiData.adx_value);
    const cci_normalized = this.normalizeCCI(kpiData.cci_value);

    // Support/Resistance normalization
    const pivot_classic_normalized = this.normalizePivotClassic(currentPrice, kpiData.classic_pivot, kpiData.classic_r1, kpiData.classic_s1);
    const pivot_fibonacci_normalized = this.normalizePivotFibonacci(currentPrice, kpiData.fibonacci_pivot, kpiData.fibonacci_r1, kpiData.fibonacci_s1);
    const pivot_camarilla_normalized = this.normalizePivotCamarilla(currentPrice, kpiData.camarilla_pivot, kpiData.camarilla_r1, kpiData.camarilla_s1);
    const pivot_woodie_normalized = this.normalizePivotWoodie(currentPrice, kpiData.woodie_pivot, kpiData.woodie_r1, kpiData.woodie_s1);
    const pivot_demark_normalized = this.normalizePivotDeMark(currentPrice, kpiData.demark_pivot, kpiData.demark_r1, kpiData.demark_s1);

    // Calculate composite scores
    const momentum_score = this.calculateMomentumScore(
      kpiData.rsi_value, kpiData.stochastic_value, kpiData.stochrsi_value,
      kpiData.williams_r_value, kpiData.roc_value, kpiData.ultimate_oscillator_value
    );

    const trend_score = this.calculateTrendScore(
      macd_normalized,
      ma_trend_5_10_normalized,
      ma_trend_10_20_normalized,
      ma_trend_20_50_normalized,
      ma_trend_50_100_normalized,
      ma_trend_100_200_normalized,
      ma_trend_20_200_normalized,
      ma_trend_50_200_normalized,
      bull_bear_power_normalized
    );

    const volatility_score = this.calculateVolatilityScore(atr_normalized, highs_lows_normalized);
    const strength_score = this.calculateStrengthScore(adx_normalized, cci_normalized);
    const support_resistance_score = this.calculateSupportResistanceScore(
      pivot_classic_normalized,
      pivot_fibonacci_normalized,
      pivot_camarilla_normalized,
      pivot_woodie_normalized,
      pivot_demark_normalized
    );

    const overall_score = this.calculateOverallScore(
      momentum_score, trend_score, volatility_score, strength_score, support_resistance_score
    );

    return {
      ticker: kpiData.ticker,
      fetch_date: kpiData.fetch_date,
      fetch_time: kpiData.fetch_time,
      rsi_normalized,
      stochastic_normalized,
      stochrsi_normalized,
      williams_r_normalized,
      roc_normalized,
      ultimate_oscillator_normalized,
      macd_normalized,
      ma_trend_5_10_normalized,
      ma_trend_10_20_normalized,
      ma_trend_20_50_normalized,
      ma_trend_20_200_normalized,
      ma_trend_50_100_normalized,
      ma_trend_100_200_normalized,
      ma_trend_50_200_normalized,
      bull_bear_power_normalized,
      atr_normalized,
      highs_lows_normalized,
      adx_normalized,
      cci_normalized,
      pivot_classic_normalized,
      pivot_fibonacci_normalized,
      pivot_camarilla_normalized,
      pivot_woodie_normalized,
      pivot_demark_normalized,
      momentum_score,
      trend_score,
      volatility_score,
      strength_score,
      support_resistance_score,
      overall_score
    };
  }
}

module.exports = NormalizationCalculator;
