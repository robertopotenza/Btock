/**
 * Normalization Integration Module
 * Integrates the normalization system with the existing Btock data pipeline
 */

const DatabaseManager = require('./database');
const NormalizationCalculator = require('./normalization');
const DataParser = require('./dataParser');

class NormalizationIntegration {
  constructor() {
    this.db = new DatabaseManager();
    this.calculator = new NormalizationCalculator();
    this.parser = new DataParser();
    this.isInitialized = false;
  }

  /**
   * Initialize the normalization system
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      await this.db.initialize();
      this.isInitialized = true;
      console.log('Normalization system initialized successfully');
    } catch (error) {
      console.error('Failed to initialize normalization system:', error);
      throw error;
    }
  }

  /**
   * Process Grok API response and store both raw and normalized data
   */
  async processGrokResponse(grokResponse, tickerLimit = null) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      console.log('Processing Grok response for normalization...');
      
      // Parse the Grok response into KPI data
      const kpiDataArray = this.parser.parseGrokResponse(grokResponse);
      
      if (kpiDataArray.length === 0) {
        console.warn('No valid KPI data found in Grok response');
        return { processed: 0, normalized: 0 };
      }

      // Prepare data for database
      const validKpiData = this.parser.prepareForDatabase(kpiDataArray);
      console.log(`Processing ${validKpiData.length} valid KPI records`);

      let processedCount = 0;
      let normalizedCount = 0;

      // Process each KPI record
      for (const kpiData of validKpiData) {
        try {
          // Insert raw KPI data
          const kpiDataId = await this.db.insertKpiData(kpiData);
          processedCount++;

          // Calculate normalized values
          const normalizedData = this.calculator.normalizeKpiData(kpiData);
          
          // Insert normalized data
          await this.db.insertNormalization(kpiDataId, normalizedData);
          normalizedCount++;

          console.log(`Processed and normalized data for ${kpiData.ticker}`);

        } catch (error) {
          console.error(`Error processing ${kpiData.ticker}:`, error.message);
        }
      }

      console.log(`Successfully processed ${processedCount} records, normalized ${normalizedCount} records`);
      
      return {
        processed: processedCount,
        normalized: normalizedCount,
        total: kpiDataArray.length
      };

    } catch (error) {
      console.error('Error processing Grok response:', error);
      throw error;
    }
  }

  /**
   * Get normalized data for specific tickers
   */
  async getNormalizedData(tickers = null, date = null) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      if (Array.isArray(tickers)) {
        // Get data for multiple tickers
        const results = [];
        for (const ticker of tickers) {
          const data = await this.db.getNormalizedData(ticker, date);
          results.push(...data);
        }
        return results;
      } else if (tickers) {
        // Get data for single ticker
        return await this.db.getNormalizedData(tickers, date);
      } else {
        // Get all data (use with caution for large datasets)
        return await this.db.getNormalizedData(null, date);
      }
    } catch (error) {
      console.error('Error getting normalized data:', error);
      throw error;
    }
  }

  /**
   * Retrieve the complete normalized dataset (raw + normalized columns)
   */
  async getFullNormalizedDataset(date = null) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      return await this.db.getFullNormalizedDataset(date);
    } catch (error) {
      console.error('Error retrieving full normalized dataset:', error);
      throw error;
    }
  }

  /**
   * Get top performing tickers based on overall score
   */
  async getTopPerformers(limit = 10, date = null) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      return await this.db.getTopPerformers(limit, date);
    } catch (error) {
      console.error('Error getting top performers:', error);
      throw error;
    }
  }

  /**
   * Get normalized scores summary for dashboard
   */
  async getScoresSummary(date = null) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      // Get top performers in each category
      const topMomentum = await this.db.db.all(`
        SELECT ticker, momentum_score 
        FROM normalization 
        WHERE momentum_score IS NOT NULL 
        ${date ? 'AND fetch_date = ?' : ''}
        ORDER BY momentum_score DESC 
        LIMIT 5
      `, date ? [date] : []);

      const topTrend = await this.db.db.all(`
        SELECT ticker, trend_score 
        FROM normalization 
        WHERE trend_score IS NOT NULL 
        ${date ? 'AND fetch_date = ?' : ''}
        ORDER BY trend_score DESC 
        LIMIT 5
      `, date ? [date] : []);

      const topOverall = await this.db.getTopPerformers(5, date);

      return {
        topMomentum,
        topTrend,
        topOverall,
        summary: {
          totalRecords: await this.getTotalRecords(date),
          lastUpdate: await this.getLastUpdateTime()
        }
      };

    } catch (error) {
      console.error('Error getting scores summary:', error);
      throw error;
    }
  }

  /**
   * Get total number of normalized records
   */
  async getTotalRecords(date = null) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    return new Promise((resolve, reject) => {
      const sql = `SELECT COUNT(*) as count FROM normalization ${date ? 'WHERE fetch_date = ?' : ''}`;
      const params = date ? [date] : [];

      this.db.db.get(sql, params, (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row.count);
        }
      });
    });
  }

  /**
   * Get last update time
   */
  async getLastUpdateTime() {
    if (!this.isInitialized) {
      await this.initialize();
    }

    return new Promise((resolve, reject) => {
      const sql = 'SELECT MAX(calculation_time) as last_update FROM normalization';

      this.db.db.get(sql, [], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row.last_update);
        }
      });
    });
  }

  /**
   * Export normalized data to Excel format
   */
  async exportNormalizedData(tickers = null, date = null) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      const data = await this.getNormalizedData(tickers, date);
      
      // Transform data for Excel export
      const excelData = data.map(record => ({
        Ticker: record.ticker,
        Company: record.company_name,
        Date: record.fetch_date,
        'Overall Score': record.overall_score?.toFixed(4) || 'N/A',
        'Momentum Score': record.momentum_score?.toFixed(4) || 'N/A',
        'Trend Score': record.trend_score?.toFixed(4) || 'N/A',
        'Volatility Score': record.volatility_score?.toFixed(4) || 'N/A',
        'Strength Score': record.strength_score?.toFixed(4) || 'N/A',
        'Support/Resistance Score': record.support_resistance_score?.toFixed(4) || 'N/A',
        'RSI Normalized': record.rsi_normalized?.toFixed(4) || 'N/A',
        'MACD Normalized': record.macd_normalized?.toFixed(4) || 'N/A',
        'ADX Normalized': record.adx_normalized?.toFixed(4) || 'N/A',
        'ATR Normalized': record.atr_normalized?.toFixed(4) || 'N/A'
      }));

      return excelData;

    } catch (error) {
      console.error('Error exporting normalized data:', error);
      throw error;
    }
  }

  /**
   * Clean up old data (optional maintenance function)
   */
  async cleanupOldData(daysToKeep = 30) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
      const cutoffDateStr = cutoffDate.toISOString().split('T')[0];

      return new Promise((resolve, reject) => {
        this.db.db.run(
          'DELETE FROM kpi_data WHERE fetch_date < ?',
          [cutoffDateStr],
          function(err) {
            if (err) {
              reject(err);
            } else {
              console.log(`Cleaned up ${this.changes} old records`);
              resolve(this.changes);
            }
          }
        );
      });

    } catch (error) {
      console.error('Error cleaning up old data:', error);
      throw error;
    }
  }

  /**
   * Close database connection
   */
  close() {
    if (this.db) {
      this.db.close();
    }
  }
}

module.exports = NormalizationIntegration;
