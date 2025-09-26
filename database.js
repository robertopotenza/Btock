const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

class DatabaseManager {
  constructor() {
    this.dbPath = path.join(__dirname, 'btock.db');
    this.db = null;
  }

  // Initialize database connection and create tables
  async initialize() {
    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) {
          console.error('Error opening database:', err.message);
          reject(err);
        } else {
          console.log('Connected to SQLite database');
          this.createTables()
            .then(() => resolve())
            .catch(reject);
        }
      });
    });
  }

  // Create tables from schema file
  async createTables() {
    const schemaPath = path.join(__dirname, 'database_schema.sql');
    const schema = fs.readFileSync(schemaPath, 'utf-8');
    
    // Remove comments first
    const cleanSchema = schema
      .split('\n')
      .filter(line => !line.trim().startsWith('--'))
      .join('\n')
      .replace(/\/\*[\s\S]*?\*\//g, ''); // Remove /* */ comments
    
    // Split on semicolons that are followed by whitespace or end of string
    const statements = cleanSchema
      .split(/;\s*(?=\n|$)/)
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0);

    console.log(`Found ${statements.length} SQL statements to execute`);

    return new Promise((resolve, reject) => {
      this.db.serialize(() => {
        let completed = 0;
        const total = statements.length;
        let hasError = false;

        if (total === 0) {
          resolve();
          return;
        }

        statements.forEach((statement, index) => {
          if (hasError) return;

          this.db.run(statement, (err) => {
            if (err) {
              console.error(`Error executing statement ${index + 1}:`, err.message);
              console.error('Statement:', statement.substring(0, 200) + '...');
              hasError = true;
              reject(err);
              return;
            }
            
            completed++;
            console.log(`Executed statement ${completed}/${total}`);
            if (completed === total) {
              console.log('Database tables created successfully');
              resolve();
            }
          });
        });
      });
    });
  }

  // Insert raw KPI data
  async insertKpiData(data) {
    const sql = `
      INSERT OR REPLACE INTO kpi_data (
        ticker, company_name, fetch_date, fetch_time,
        ti_summary, ti_buy_count, ti_neutral_count, ti_sell_count,
        ma_summary, ma_buy_count, ma_sell_count,
        rsi_value, rsi_action, stochastic_value, stochastic_action,
        stochrsi_value, stochrsi_action, williams_r_value, williams_r_action,
        roc_value, roc_action, ultimate_oscillator_value, ultimate_oscillator_action,
        macd_value, macd_action, macd_signal, adx_value, adx_action,
        cci_value, cci_action, bull_bear_power_value, bull_bear_power_action,
        atr_value, atr_action, highs_lows_value, highs_lows_action,
        ma20_simple_value, ma20_simple_action, ma20_exp_value, ma20_exp_action,
        ma50_simple_value, ma50_simple_action, ma50_exp_value, ma50_exp_action,
        ma200_simple_value, ma200_simple_action, ma200_exp_value, ma200_exp_action,
        classic_s2, classic_s1, classic_pivot, classic_r1, classic_r2,
        fibonacci_s1, fibonacci_pivot, fibonacci_r1,
        current_price, high_14, low_14
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    return new Promise((resolve, reject) => {
      this.db.run(sql, [
        data.ticker, data.company_name, data.fetch_date, data.fetch_time,
        data.ti_summary, data.ti_buy_count, data.ti_neutral_count, data.ti_sell_count,
        data.ma_summary, data.ma_buy_count, data.ma_sell_count,
        data.rsi_value, data.rsi_action, data.stochastic_value, data.stochastic_action,
        data.stochrsi_value, data.stochrsi_action, data.williams_r_value, data.williams_r_action,
        data.roc_value, data.roc_action, data.ultimate_oscillator_value, data.ultimate_oscillator_action,
        data.macd_value, data.macd_action, data.macd_signal, data.adx_value, data.adx_action,
        data.cci_value, data.cci_action, data.bull_bear_power_value, data.bull_bear_power_action,
        data.atr_value, data.atr_action, data.highs_lows_value, data.highs_lows_action,
        data.ma20_simple_value, data.ma20_simple_action, data.ma20_exp_value, data.ma20_exp_action,
        data.ma50_simple_value, data.ma50_simple_action, data.ma50_exp_value, data.ma50_exp_action,
        data.ma200_simple_value, data.ma200_simple_action, data.ma200_exp_value, data.ma200_exp_action,
        data.classic_s2, data.classic_s1, data.classic_pivot, data.classic_r1, data.classic_r2,
        data.fibonacci_s1, data.fibonacci_pivot, data.fibonacci_r1,
        data.current_price, data.high_14, data.low_14
      ], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(this.lastID);
        }
      });
    });
  }

  // Insert normalized data
  async insertNormalization(kpiDataId, normalizedData) {
    const sql = `
      INSERT OR REPLACE INTO normalization (
        kpi_data_id, ticker, fetch_date, fetch_time,
        rsi_normalized, stochastic_normalized, stochrsi_normalized,
        williams_r_normalized, roc_normalized, ultimate_oscillator_normalized,
        macd_normalized, ma_trend_20_50_normalized, ma_trend_50_200_normalized,
        ma_trend_20_200_normalized, bull_bear_power_normalized,
        atr_normalized, highs_lows_normalized, adx_normalized, cci_normalized,
        pivot_classic_normalized, pivot_fibonacci_normalized,
        momentum_score, trend_score, volatility_score, strength_score,
        support_resistance_score, overall_score
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    return new Promise((resolve, reject) => {
      this.db.run(sql, [
        kpiDataId, normalizedData.ticker, normalizedData.fetch_date, normalizedData.fetch_time,
        normalizedData.rsi_normalized, normalizedData.stochastic_normalized, normalizedData.stochrsi_normalized,
        normalizedData.williams_r_normalized, normalizedData.roc_normalized, normalizedData.ultimate_oscillator_normalized,
        normalizedData.macd_normalized, normalizedData.ma_trend_20_50_normalized, normalizedData.ma_trend_50_200_normalized,
        normalizedData.ma_trend_20_200_normalized, normalizedData.bull_bear_power_normalized,
        normalizedData.atr_normalized, normalizedData.highs_lows_normalized, normalizedData.adx_normalized, normalizedData.cci_normalized,
        normalizedData.pivot_classic_normalized, normalizedData.pivot_fibonacci_normalized,
        normalizedData.momentum_score, normalizedData.trend_score, normalizedData.volatility_score, normalizedData.strength_score,
        normalizedData.support_resistance_score, normalizedData.overall_score
      ], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(this.lastID);
        }
      });
    });
  }

  // Get KPI data by ticker and date
  async getKpiData(ticker, date = null) {
    let sql = 'SELECT * FROM kpi_data WHERE ticker = ?';
    let params = [ticker];

    if (date) {
      sql += ' AND fetch_date = ?';
      params.push(date);
    }

    sql += ' ORDER BY fetch_time DESC';

    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // Get normalized data with raw KPI data
  async getNormalizedData(ticker, date = null) {
    let sql = 'SELECT * FROM kpi_with_normalization WHERE ticker = ?';
    let params = [ticker];

    if (date) {
      sql += ' AND fetch_date = ?';
      params.push(date);
    }

    sql += ' ORDER BY fetch_time DESC';

    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // Get top performers by overall score
  async getTopPerformers(limit = 10, date = null) {
    let sql = `
      SELECT ticker, company_name, overall_score, momentum_score, trend_score, 
             volatility_score, strength_score, support_resistance_score, fetch_time
      FROM kpi_with_normalization 
      WHERE overall_score IS NOT NULL
    `;
    let params = [];

    if (date) {
      sql += ' AND fetch_date = ?';
      params.push(date);
    }

    sql += ' ORDER BY overall_score DESC LIMIT ?';
    params.push(limit);

    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // Close database connection
  close() {
    if (this.db) {
      this.db.close((err) => {
        if (err) {
          console.error('Error closing database:', err.message);
        } else {
          console.log('Database connection closed');
        }
      });
    }
  }
}

module.exports = DatabaseManager;
