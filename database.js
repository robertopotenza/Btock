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
              this.ensureSchemaUpgrades()
                .then(() => {
                  console.log('Database tables created successfully');
                  resolve();
                })
                .catch(reject);
            }
          });
        });
      });
    });
  }

  // Calculate average ignoring null/undefined values
  calculateAverage(values) {
    const validValues = values.filter(value => value !== null && value !== undefined && !Number.isNaN(value));
    if (validValues.length === 0) {
      return null;
    }
    const sum = validValues.reduce((acc, value) => acc + value, 0);
    return sum / validValues.length;
  }

  // Compute composite components using extended weighting formula
  computeCompositeComponents(normalizedData) {
    const momentumComponent = this.calculateAverage([
      normalizedData.rsi_normalized,
      normalizedData.stochastic_normalized,
      normalizedData.stochrsi_normalized,
      normalizedData.williams_r_normalized,
      normalizedData.roc_normalized,
      normalizedData.ultimate_oscillator_normalized
    ]);

    const trendComponent = this.calculateAverage([
      normalizedData.macd_normalized,
      normalizedData.ma_trend_5_10_normalized,
      normalizedData.ma_trend_10_20_normalized,
      normalizedData.ma_trend_20_50_normalized,
      normalizedData.ma_trend_50_100_normalized,
      normalizedData.ma_trend_100_200_normalized,
      normalizedData.ma_trend_20_200_normalized,
      normalizedData.ma_trend_50_200_normalized,
      normalizedData.bull_bear_power_normalized
    ]);

    const volatilityComponent = this.calculateAverage([
      normalizedData.atr_normalized,
      normalizedData.highs_lows_normalized
    ]);

    const strengthComponent = this.calculateAverage([
      normalizedData.adx_normalized,
      normalizedData.cci_normalized
    ]);

    const supportComponent = this.calculateAverage([
      normalizedData.pivot_classic_normalized,
      normalizedData.pivot_fibonacci_normalized,
      normalizedData.pivot_camarilla_normalized,
      normalizedData.pivot_woodie_normalized,
      normalizedData.pivot_demark_normalized
    ]);

    const weights = {
      momentum: 0.25,
      trend: 0.35,
      volatility: 0.15,
      strength: 0.15,
      support: 0.10
    };

    const contributions = [];
    let compositeScore = 0;

    if (momentumComponent !== null) {
      compositeScore += momentumComponent * weights.momentum;
      contributions.push(true);
    }

    if (trendComponent !== null) {
      compositeScore += trendComponent * weights.trend;
      contributions.push(true);
    }

    if (volatilityComponent !== null) {
      compositeScore += volatilityComponent * weights.volatility;
      contributions.push(true);
    }

    if (strengthComponent !== null) {
      compositeScore += strengthComponent * weights.strength;
      contributions.push(true);
    }

    if (supportComponent !== null) {
      compositeScore += supportComponent * weights.support;
      contributions.push(true);
    }

    return {
      momentumComponent,
      trendComponent,
      volatilityComponent,
      strengthComponent,
      supportComponent,
      compositeScore: contributions.length > 0 ? compositeScore : null
    };
  }

  // Check if a column exists in a table
  columnExists(table, column) {
    return new Promise((resolve, reject) => {
      this.db.all(`PRAGMA table_info(${table})`, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.some(row => row.name === column));
        }
      });
    });
  }

  // Add missing column definitions to legacy tables
  async addColumnIfMissing(table, column, definition) {
    const exists = await this.columnExists(table, column);
    if (!exists) {
      await new Promise((resolve, reject) => {
        this.db.run(`ALTER TABLE ${table} ADD COLUMN ${column} ${definition}`, (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        });
      });
      console.log(`Added column ${column} to ${table}`);
    }
  }

  // Apply schema upgrades for newly introduced columns
  async ensureSchemaUpgrades() {
    const kpiColumns = [
      { column: 'ma5_simple_value', definition: 'DECIMAL(10,4)' },
      { column: 'ma5_simple_action', definition: 'VARCHAR(20)' },
      { column: 'ma5_exp_value', definition: 'DECIMAL(10,4)' },
      { column: 'ma5_exp_action', definition: 'VARCHAR(20)' },
      { column: 'ma10_simple_value', definition: 'DECIMAL(10,4)' },
      { column: 'ma10_simple_action', definition: 'VARCHAR(20)' },
      { column: 'ma10_exp_value', definition: 'DECIMAL(10,4)' },
      { column: 'ma10_exp_action', definition: 'VARCHAR(20)' },
      { column: 'ma100_simple_value', definition: 'DECIMAL(10,4)' },
      { column: 'ma100_simple_action', definition: 'VARCHAR(20)' },
      { column: 'ma100_exp_value', definition: 'DECIMAL(10,4)' },
      { column: 'ma100_exp_action', definition: 'VARCHAR(20)' },
      { column: 'classic_s3', definition: 'DECIMAL(10,4)' },
      { column: 'classic_r3', definition: 'DECIMAL(10,4)' },
      { column: 'fibonacci_s2', definition: 'DECIMAL(10,4)' },
      { column: 'fibonacci_s3', definition: 'DECIMAL(10,4)' },
      { column: 'fibonacci_r2', definition: 'DECIMAL(10,4)' },
      { column: 'fibonacci_r3', definition: 'DECIMAL(10,4)' },
      { column: 'camarilla_s3', definition: 'DECIMAL(10,4)' },
      { column: 'camarilla_s2', definition: 'DECIMAL(10,4)' },
      { column: 'camarilla_s1', definition: 'DECIMAL(10,4)' },
      { column: 'camarilla_pivot', definition: 'DECIMAL(10,4)' },
      { column: 'camarilla_r1', definition: 'DECIMAL(10,4)' },
      { column: 'camarilla_r2', definition: 'DECIMAL(10,4)' },
      { column: 'camarilla_r3', definition: 'DECIMAL(10,4)' },
      { column: 'woodie_s3', definition: 'DECIMAL(10,4)' },
      { column: 'woodie_s2', definition: 'DECIMAL(10,4)' },
      { column: 'woodie_s1', definition: 'DECIMAL(10,4)' },
      { column: 'woodie_pivot', definition: 'DECIMAL(10,4)' },
      { column: 'woodie_r1', definition: 'DECIMAL(10,4)' },
      { column: 'woodie_r2', definition: 'DECIMAL(10,4)' },
      { column: 'woodie_r3', definition: 'DECIMAL(10,4)' },
      { column: 'demark_s1', definition: 'DECIMAL(10,4)' },
      { column: 'demark_pivot', definition: 'DECIMAL(10,4)' },
      { column: 'demark_r1', definition: 'DECIMAL(10,4)' }
    ];

    for (const { column, definition } of kpiColumns) {
      await this.addColumnIfMissing('kpi_data', column, definition);
    }

    const normalizationColumns = [
      { column: 'ma_trend_5_10_normalized', definition: 'DECIMAL(10,6)' },
      { column: 'ma_trend_10_20_normalized', definition: 'DECIMAL(10,6)' },
      { column: 'ma_trend_50_100_normalized', definition: 'DECIMAL(10,6)' },
      { column: 'ma_trend_100_200_normalized', definition: 'DECIMAL(10,6)' },
      { column: 'ma_trend_50_200_normalized', definition: 'DECIMAL(10,6)' },
      { column: 'pivot_camarilla_normalized', definition: 'DECIMAL(10,6)' },
      { column: 'pivot_woodie_normalized', definition: 'DECIMAL(10,6)' },
      { column: 'pivot_demark_normalized', definition: 'DECIMAL(10,6)' }
    ];

    for (const { column, definition } of normalizationColumns) {
      await this.addColumnIfMissing('normalization', column, definition);
    }
  }

  // Insert or update ticker composite score
  async upsertTickerCompositeScore(normalizationId, normalizedData) {
    const {
      momentumComponent,
      trendComponent,
      volatilityComponent,
      strengthComponent,
      supportComponent,
      compositeScore
    } = this.computeCompositeComponents(normalizedData);

    const sql = `
      INSERT OR REPLACE INTO ticker_composite_scores (
        normalization_id, ticker, fetch_date, fetch_time,
        momentum_component, trend_component, volatility_component,
        strength_component, support_resistance_component, composite_score
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    return new Promise((resolve, reject) => {
      this.db.run(sql, [
        normalizationId,
        normalizedData.ticker,
        normalizedData.fetch_date,
        normalizedData.fetch_time,
        momentumComponent,
        trendComponent,
        volatilityComponent,
        strengthComponent,
        supportComponent,
        compositeScore
      ], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(this.lastID);
        }
      });
    });
  }

  // Insert raw KPI data
  async insertKpiData(data) {
    const sql = `
      INSERT OR REPLACE INTO kpi_data (
        ticker, company_name, fetch_date, fetch_time,
        ti_summary, ti_buy_count, ti_neutral_count, ti_sell_count,
        ma_summary, ma_buy_count, ma_sell_count, rsi_value,
        rsi_action, stochastic_value, stochastic_action, stochrsi_value,
        stochrsi_action, williams_r_value, williams_r_action, roc_value,
        roc_action, ultimate_oscillator_value, ultimate_oscillator_action, macd_value,
        macd_action, macd_signal, adx_value, adx_action,
        cci_value, cci_action, bull_bear_power_value, bull_bear_power_action,
        atr_value, atr_action, highs_lows_value, highs_lows_action,
        ma5_simple_value, ma5_simple_action, ma5_exp_value, ma5_exp_action,
        ma10_simple_value, ma10_simple_action, ma10_exp_value, ma10_exp_action,
        ma20_simple_value, ma20_simple_action, ma20_exp_value, ma20_exp_action,
        ma50_simple_value, ma50_simple_action, ma50_exp_value, ma50_exp_action,
        ma100_simple_value, ma100_simple_action, ma100_exp_value, ma100_exp_action,
        ma200_simple_value, ma200_simple_action, ma200_exp_value, ma200_exp_action,
        classic_s3, classic_s2, classic_s1, classic_pivot,
        classic_r1, classic_r2, classic_r3, fibonacci_s3,
        fibonacci_s2, fibonacci_s1, fibonacci_pivot, fibonacci_r1,
        fibonacci_r2, fibonacci_r3, camarilla_s3, camarilla_s2,
        camarilla_s1, camarilla_pivot, camarilla_r1, camarilla_r2,
        camarilla_r3, woodie_s3, woodie_s2, woodie_s1,
        woodie_pivot, woodie_r1, woodie_r2, woodie_r3,
        demark_s1, demark_pivot, demark_r1, current_price,
        high_14, low_14
      ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?
      )
    `;

    return new Promise((resolve, reject) => {
      this.db.run(sql, [
        data.ticker,
        data.company_name,
        data.fetch_date,
        data.fetch_time,
        data.ti_summary,
        data.ti_buy_count,
        data.ti_neutral_count,
        data.ti_sell_count,
        data.ma_summary,
        data.ma_buy_count,
        data.ma_sell_count,
        data.rsi_value,
        data.rsi_action,
        data.stochastic_value,
        data.stochastic_action,
        data.stochrsi_value,
        data.stochrsi_action,
        data.williams_r_value,
        data.williams_r_action,
        data.roc_value,
        data.roc_action,
        data.ultimate_oscillator_value,
        data.ultimate_oscillator_action,
        data.macd_value,
        data.macd_action,
        data.macd_signal,
        data.adx_value,
        data.adx_action,
        data.cci_value,
        data.cci_action,
        data.bull_bear_power_value,
        data.bull_bear_power_action,
        data.atr_value,
        data.atr_action,
        data.highs_lows_value,
        data.highs_lows_action,
        data.ma5_simple_value,
        data.ma5_simple_action,
        data.ma5_exp_value,
        data.ma5_exp_action,
        data.ma10_simple_value,
        data.ma10_simple_action,
        data.ma10_exp_value,
        data.ma10_exp_action,
        data.ma20_simple_value,
        data.ma20_simple_action,
        data.ma20_exp_value,
        data.ma20_exp_action,
        data.ma50_simple_value,
        data.ma50_simple_action,
        data.ma50_exp_value,
        data.ma50_exp_action,
        data.ma100_simple_value,
        data.ma100_simple_action,
        data.ma100_exp_value,
        data.ma100_exp_action,
        data.ma200_simple_value,
        data.ma200_simple_action,
        data.ma200_exp_value,
        data.ma200_exp_action,
        data.classic_s3,
        data.classic_s2,
        data.classic_s1,
        data.classic_pivot,
        data.classic_r1,
        data.classic_r2,
        data.classic_r3,
        data.fibonacci_s3,
        data.fibonacci_s2,
        data.fibonacci_s1,
        data.fibonacci_pivot,
        data.fibonacci_r1,
        data.fibonacci_r2,
        data.fibonacci_r3,
        data.camarilla_s3,
        data.camarilla_s2,
        data.camarilla_s1,
        data.camarilla_pivot,
        data.camarilla_r1,
        data.camarilla_r2,
        data.camarilla_r3,
        data.woodie_s3,
        data.woodie_s2,
        data.woodie_s1,
        data.woodie_pivot,
        data.woodie_r1,
        data.woodie_r2,
        data.woodie_r3,
        data.demark_s1,
        data.demark_pivot,
        data.demark_r1,
        data.current_price,
        data.high_14,
        data.low_14
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
        macd_normalized, ma_trend_5_10_normalized, ma_trend_10_20_normalized,
        ma_trend_20_50_normalized, ma_trend_50_100_normalized,
        ma_trend_100_200_normalized, ma_trend_20_200_normalized,
        ma_trend_50_200_normalized, bull_bear_power_normalized,
        atr_normalized, highs_lows_normalized, adx_normalized, cci_normalized,
        pivot_classic_normalized, pivot_fibonacci_normalized,
        pivot_camarilla_normalized, pivot_woodie_normalized, pivot_demark_normalized,
        momentum_score, trend_score, volatility_score, strength_score,
        support_resistance_score, overall_score
      ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?
      )
    `;

    return new Promise((resolve, reject) => {
      this.db.run(sql, [
        kpiDataId, normalizedData.ticker, normalizedData.fetch_date, normalizedData.fetch_time,
        normalizedData.rsi_normalized, normalizedData.stochastic_normalized, normalizedData.stochrsi_normalized,
        normalizedData.williams_r_normalized, normalizedData.roc_normalized, normalizedData.ultimate_oscillator_normalized,
        normalizedData.macd_normalized, normalizedData.ma_trend_5_10_normalized, normalizedData.ma_trend_10_20_normalized,
        normalizedData.ma_trend_20_50_normalized, normalizedData.ma_trend_50_100_normalized,
        normalizedData.ma_trend_100_200_normalized, normalizedData.ma_trend_20_200_normalized,
        normalizedData.ma_trend_50_200_normalized, normalizedData.bull_bear_power_normalized,
        normalizedData.atr_normalized, normalizedData.highs_lows_normalized, normalizedData.adx_normalized, normalizedData.cci_normalized,
        normalizedData.pivot_classic_normalized, normalizedData.pivot_fibonacci_normalized,
        normalizedData.pivot_camarilla_normalized, normalizedData.pivot_woodie_normalized, normalizedData.pivot_demark_normalized,
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

  // Get the complete kpi_with_normalization dataset
  async getFullNormalizedDataset(date = null) {
    let sql = 'SELECT * FROM kpi_with_normalization';
    const params = [];

    if (date) {
      sql += ' WHERE fetch_date = ?';
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
