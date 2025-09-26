/**
 * API Routes for Normalization Data
 * Provides endpoints to access normalized KPI data
 */

const express = require('express');
const router = express.Router();

// Initialize normalization system (will be passed from main server)
let normalization = null;

const initializeRoutes = (normalizationInstance) => {
  normalization = normalizationInstance;
  return router;
};

// Get all normalized data
router.get('/normalized', async (req, res) => {
  try {
    const { date, limit } = req.query;

    if (!normalization) {
      return res.status(500).json({ error: 'Normalization system not initialized' });
    }

    // Get all data with optional limit
    let data = await normalization.getNormalizedData(null, date);
    if (limit) {
      const limitNum = parseInt(limit);
      if (!isNaN(limitNum) && limitNum > 0) {
        data = data.slice(0, limitNum);
      }
    }

    res.json({
      success: true,
      data,
      count: data.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching normalized data:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get normalized data for specific ticker
router.get('/normalized/:ticker', async (req, res) => {
  try {
    const { ticker } = req.params;
    const { date } = req.query;

    if (!normalization) {
      return res.status(500).json({ error: 'Normalization system not initialized' });
    }

    const data = await normalization.getNormalizedData(ticker, date);

    res.json({
      success: true,
      data,
      count: data.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching normalized data:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get top performers by overall score
router.get('/top-performers', async (req, res) => {
  try {
    const { limit = 10, date } = req.query;

    if (!normalization) {
      return res.status(500).json({ error: 'Normalization system not initialized' });
    }

    const limitNum = parseInt(limit);
    const data = await normalization.getTopPerformers(limitNum, date);

    res.json({
      success: true,
      data,
      count: data.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching top performers:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get scores summary for dashboard
router.get('/scores-summary', async (req, res) => {
  try {
    const { date } = req.query;

    if (!normalization) {
      return res.status(500).json({ error: 'Normalization system not initialized' });
    }

    const summary = await normalization.getScoresSummary(date);

    res.json({
      success: true,
      data: summary,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching scores summary:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Export normalized data to Excel
router.get('/export/normalized', async (req, res) => {
  try {
    const { tickers, date, format = 'json' } = req.query;

    if (!normalization) {
      return res.status(500).json({ error: 'Normalization system not initialized' });
    }

    const tickerArray = tickers ? tickers.split(',') : null;
    const data = await normalization.exportNormalizedData(tickerArray, date);

    if (format === 'excel') {
      // Create Excel workbook
      const ExcelJS = require('exceljs');
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet('Normalized KPI Data');

      // Add headers
      if (data.length > 0) {
        const headers = Object.keys(data[0]);
        worksheet.addRow(headers);

        // Add data rows
        data.forEach(row => {
          const values = headers.map(header => row[header]);
          worksheet.addRow(values);
        });

        // Style the header row
        const headerRow = worksheet.getRow(1);
        headerRow.font = { bold: true };
        headerRow.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFE0E0E0' }
        };
      }

      // Set response headers for Excel download
      res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
      res.setHeader('Content-Disposition', `attachment; filename=normalized_kpi_data_${new Date().toISOString().split('T')[0]}.xlsx`);

      // Write to response
      await workbook.xlsx.write(res);
      res.end();

    } else {
      // Return JSON format
      res.json({
        success: true,
        data,
        count: data.length,
        timestamp: new Date().toISOString()
      });
    }

  } catch (error) {
    console.error('Error exporting normalized data:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get normalization statistics
router.get('/stats', async (req, res) => {
  try {
    const { date } = req.query;

    if (!normalization) {
      return res.status(500).json({ error: 'Normalization system not initialized' });
    }

    const totalRecords = await normalization.getTotalRecords(date);
    const lastUpdate = await normalization.getLastUpdateTime();

    res.json({
      success: true,
      data: {
        totalRecords,
        lastUpdate,
        date: date || 'all'
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching normalization stats:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Health check for normalization system
router.get('/health', async (req, res) => {
  try {
    if (!normalization) {
      return res.status(500).json({
        success: false,
        status: 'error',
        message: 'Normalization system not initialized'
      });
    }

    // Try to get a simple count to test database connectivity
    const totalRecords = await normalization.getTotalRecords();

    res.json({
      success: true,
      status: 'healthy',
      data: {
        totalRecords,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    console.error('Normalization health check failed:', error);
    res.status(500).json({
      success: false,
      status: 'error',
      message: error.message
    });
  }
});

module.exports = { router, initializeRoutes };
