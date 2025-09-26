/**
 * Data Parser for converting Grok API response to database format
 * Handles parsing of markdown table data into structured KPI objects
 */

const { marked } = require('marked');

class DataParser {
  constructor() {
    this.columnMapping = {
      // Basic info
      'Ticker': 'ticker',
      'Company_Name': 'company_name',
      
      // Summary data
      'TI_Summary': 'ti_summary',
      'TI_Buy_Count': 'ti_buy_count',
      'TI_Neutral_Count': 'ti_neutral_count',
      'TI_Sell_Count': 'ti_sell_count',
      'MA_Summary': 'ma_summary',
      'MA_Buy_Count': 'ma_buy_count',
      'MA_Sell_Count': 'ma_sell_count',
      
      // Oscillators
      'RSI_Value': 'rsi_value',
      'RSI_Action': 'rsi_action',
      'Stochastic_Value': 'stochastic_value',
      'Stochastic_Action': 'stochastic_action',
      'StochRSI_Value': 'stochrsi_value',
      'StochRSI_Action': 'stochrsi_action',
      'Williams_R_Value': 'williams_r_value',
      'Williams_R_Action': 'williams_r_action',
      'ROC_Value': 'roc_value',
      'ROC_Action': 'roc_action',
      'Ultimate_Oscillator_Value': 'ultimate_oscillator_value',
      'Ultimate_Oscillator_Action': 'ultimate_oscillator_action',

      // Trend indicators
      'MACD_Value': 'macd_value',
      'MACD_Action': 'macd_action',
      'MACD_Signal': 'macd_signal',
      'Bull_Bear_Power_Value': 'bull_bear_power_value',
      'Bull_Bear_Power_Action': 'bull_bear_power_action',
      'ADX_Value': 'adx_value',
      'ADX_Action': 'adx_action',
      'CCI_Value': 'cci_value',
      'CCI_Action': 'cci_action',

      // Moving averages
      'MA5_Simple_Value': 'ma5_simple_value',
      'MA5_Simple_Action': 'ma5_simple_action',
      'MA5_Exp_Value': 'ma5_exp_value',
      'MA5_Exp_Action': 'ma5_exp_action',
      'MA10_Simple_Value': 'ma10_simple_value',
      'MA10_Simple_Action': 'ma10_simple_action',
      'MA10_Exp_Value': 'ma10_exp_value',
      'MA10_Exp_Action': 'ma10_exp_action',
      'MA20_Simple_Value': 'ma20_simple_value',
      'MA20_Simple_Action': 'ma20_simple_action',
      'MA20_Exp_Value': 'ma20_exp_value',
      'MA20_Exp_Action': 'ma20_exp_action',
      'MA50_Simple_Value': 'ma50_simple_value',
      'MA50_Simple_Action': 'ma50_simple_action',
      'MA50_Exp_Value': 'ma50_exp_value',
      'MA50_Exp_Action': 'ma50_exp_action',
      'MA100_Simple_Value': 'ma100_simple_value',
      'MA100_Simple_Action': 'ma100_simple_action',
      'MA100_Exp_Value': 'ma100_exp_value',
      'MA100_Exp_Action': 'ma100_exp_action',
      'MA200_Simple_Value': 'ma200_simple_value',
      'MA200_Simple_Action': 'ma200_simple_action',
      'MA200_Exp_Value': 'ma200_exp_value',
      'MA200_Exp_Action': 'ma200_exp_action',

      // Pivot points
      'Classic_S3': 'classic_s3',
      'Classic_S2': 'classic_s2',
      'Classic_S1': 'classic_s1',
      'Classic_Pivot': 'classic_pivot',
      'Classic_R1': 'classic_r1',
      'Classic_R2': 'classic_r2',
      'Classic_R3': 'classic_r3',
      'Fibonacci_S3': 'fibonacci_s3',
      'Fibonacci_S2': 'fibonacci_s2',
      'Fibonacci_S1': 'fibonacci_s1',
      'Fibonacci_Pivot': 'fibonacci_pivot',
      'Fibonacci_R1': 'fibonacci_r1',
      'Fibonacci_R2': 'fibonacci_r2',
      'Fibonacci_R3': 'fibonacci_r3',
      'Camarilla_S3': 'camarilla_s3',
      'Camarilla_S2': 'camarilla_s2',
      'Camarilla_S1': 'camarilla_s1',
      'Camarilla_Pivot': 'camarilla_pivot',
      'Camarilla_R1': 'camarilla_r1',
      'Camarilla_R2': 'camarilla_r2',
      'Camarilla_R3': 'camarilla_r3',
      'Woodie_S3': 'woodie_s3',
      'Woodie_S2': 'woodie_s2',
      'Woodie_S1': 'woodie_s1',
      'Woodie_Pivot': 'woodie_pivot',
      'Woodie_R1': 'woodie_r1',
      'Woodie_R2': 'woodie_r2',
      'Woodie_R3': 'woodie_r3',
      'DeMark_S1': 'demark_s1',
      'DeMark_Pivot': 'demark_pivot',
      'DeMark_R1': 'demark_r1'
    };
  }

  /**
   * Extract plain text from markdown cell
   */
  extractPlainText(cell) {
    if (cell === null || cell === undefined) {
      return '';
    }

    if (typeof cell === 'string') {
      return cell.trim();
    }

    if (typeof cell.text === 'string') {
      return cell.text.trim();
    }

    if (Array.isArray(cell.tokens)) {
      const text = cell.tokens
        .map((token) => {
          if (token.type === 'text' || token.type === 'escape' || token.type === 'codespan') {
            return token.text || '';
          }

          if (token.type === 'link' || token.type === 'strong' || token.type === 'em' || token.type === 'del') {
            return this.extractPlainText({ tokens: token.tokens || [], text: token.text });
          }

          if (token.type === 'space') {
            return ' ';
          }

          if (token.type === 'br') {
            return '\n';
          }

          return token.raw || '';
        })
        .join('');

      return text.trim();
    }

    return String(cell).trim();
  }

  /**
   * Parse markdown table into structured data
   */
  parseMarkdownTable(markdown) {
    if (!markdown) {
      return { headers: [], rows: [] };
    }

    const tokens = marked.lexer(markdown);
    const tableToken = tokens.find((token) => token.type === 'table' && token.header?.length);

    if (!tableToken) {
      console.warn('No table found in markdown content');
      return { headers: [], rows: [] };
    }

    const headers = tableToken.header.map((cell) => this.extractPlainText(cell));
    const rows = tableToken.rows.map((row) =>
      row.map((cell) => this.extractPlainText(cell))
    );

    return { headers, rows };
  }

  /**
   * Convert table row to KPI data object
   */
  rowToKpiData(headers, row, fetchDate, fetchTime) {
    const kpiData = {
      fetch_date: fetchDate,
      fetch_time: fetchTime,
      // Initialize all fields to null
      ticker: null,
      company_name: null,
      ti_summary: null,
      ti_buy_count: null,
      ti_neutral_count: null,
      ti_sell_count: null,
      ma_summary: null,
      ma_buy_count: null,
      ma_sell_count: null,
      rsi_value: null,
      rsi_action: null,
      stochastic_value: null,
      stochastic_action: null,
      stochrsi_value: null,
      stochrsi_action: null,
      williams_r_value: null,
      williams_r_action: null,
      roc_value: null,
      roc_action: null,
      ultimate_oscillator_value: null,
      ultimate_oscillator_action: null,
      macd_value: null,
      macd_action: null,
      macd_signal: null, // Will need to be extracted or calculated
      adx_value: null,
      adx_action: null,
      cci_value: null,
      cci_action: null,
      bull_bear_power_value: null,
      bull_bear_power_action: null,
      atr_value: null,
      atr_action: null,
      highs_lows_value: null,
      highs_lows_action: null,
      ma5_simple_value: null,
      ma5_simple_action: null,
      ma5_exp_value: null,
      ma5_exp_action: null,
      ma10_simple_value: null,
      ma10_simple_action: null,
      ma10_exp_value: null,
      ma10_exp_action: null,
      ma20_simple_value: null,
      ma20_simple_action: null,
      ma20_exp_value: null,
      ma20_exp_action: null,
      ma50_simple_value: null,
      ma50_simple_action: null,
      ma50_exp_value: null,
      ma50_exp_action: null,
      ma100_simple_value: null,
      ma100_simple_action: null,
      ma100_exp_value: null,
      ma100_exp_action: null,
      ma200_simple_value: null,
      ma200_simple_action: null,
      ma200_exp_value: null,
      ma200_exp_action: null,
      classic_s3: null,
      classic_s2: null,
      classic_s1: null,
      classic_pivot: null,
      classic_r1: null,
      classic_r2: null,
      classic_r3: null,
      fibonacci_s3: null,
      fibonacci_s2: null,
      fibonacci_s1: null,
      fibonacci_pivot: null,
      fibonacci_r1: null,
      fibonacci_r2: null,
      fibonacci_r3: null,
      camarilla_s3: null,
      camarilla_s2: null,
      camarilla_s1: null,
      camarilla_pivot: null,
      camarilla_r1: null,
      camarilla_r2: null,
      camarilla_r3: null,
      woodie_s3: null,
      woodie_s2: null,
      woodie_s1: null,
      woodie_pivot: null,
      woodie_r1: null,
      woodie_r2: null,
      woodie_r3: null,
      demark_s1: null,
      demark_pivot: null,
      demark_r1: null,
      current_price: null,
      high_14: null,
      low_14: null
    };

    // Map table columns to KPI data fields
    headers.forEach((header, index) => {
      const fieldName = this.columnMapping[header];
      if (fieldName && index < row.length) {
        let value = row[index];
        
        // Clean up the value
        if (value === 'N/A' || value === '' || value === '-') {
          value = null;
        } else if (fieldName.includes('_count') || fieldName.includes('_value') ||
                   fieldName.includes('_s1') || fieldName.includes('_s2') || fieldName.includes('_s3') ||
                   fieldName.includes('_r1') || fieldName.includes('_r2') || fieldName.includes('_r3') ||
                   fieldName.includes('_pivot')) {
          // Parse numeric values
          const numericValue = parseFloat(value);
          value = isNaN(numericValue) ? null : numericValue;
        }
        
        kpiData[fieldName] = value;
      }
    });

    // Estimate current price from moving averages if not available
    if (!kpiData.current_price) {
      kpiData.current_price = kpiData.ma20_simple_value || kpiData.ma50_simple_value || kpiData.ma200_simple_value;
    }

    // Estimate MACD signal (typically MACD signal is close to MACD value)
    if (kpiData.macd_value && !kpiData.macd_signal) {
      kpiData.macd_signal = kpiData.macd_value * 0.9; // Rough approximation
    }

    return kpiData;
  }

  /**
   * Parse complete Grok API response into KPI data array
   */
  parseGrokResponse(grokResponse) {
    const fetchTime = new Date().toISOString();
    const fetchDate = fetchTime.split('T')[0];

    try {
      const { headers, rows } = this.parseMarkdownTable(grokResponse.raw);
      
      if (headers.length === 0 || rows.length === 0) {
        console.warn('No valid table data found in Grok response');
        return [];
      }

      console.log(`Parsed ${rows.length} rows with ${headers.length} columns`);
      
      const kpiDataArray = rows.map(row => 
        this.rowToKpiData(headers, row, fetchDate, fetchTime)
      ).filter(kpiData => kpiData.ticker); // Filter out rows without ticker

      console.log(`Successfully parsed ${kpiDataArray.length} valid KPI records`);
      return kpiDataArray;

    } catch (error) {
      console.error('Error parsing Grok response:', error);
      return [];
    }
  }

  /**
   * Validate KPI data before database insertion
   */
  validateKpiData(kpiData) {
    const errors = [];

    if (!kpiData.ticker) {
      errors.push('Missing ticker symbol');
    }

    if (!kpiData.fetch_date) {
      errors.push('Missing fetch date');
    }

    if (!kpiData.fetch_time) {
      errors.push('Missing fetch time');
    }

    // Check if at least some KPI values are present
    const kpiFields = [
      'rsi_value', 'stochastic_value', 'macd_value', 'adx_value',
      'ma20_simple_value', 'ma50_simple_value', 'ma200_simple_value'
    ];

    const hasKpiData = kpiFields.some(field => kpiData[field] !== null);
    if (!hasKpiData) {
      errors.push('No valid KPI values found');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Clean and prepare KPI data for database insertion
   */
  prepareForDatabase(kpiDataArray) {
    return kpiDataArray
      .map(kpiData => {
        const validation = this.validateKpiData(kpiData);
        if (!validation.isValid) {
          console.warn(`Invalid KPI data for ${kpiData.ticker}:`, validation.errors);
          return null;
        }
        return kpiData;
      })
      .filter(kpiData => kpiData !== null);
  }
}

module.exports = DataParser;
