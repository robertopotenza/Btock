/**
 * Comprehensive Test Suite for Normalization System
 * Tests all components: database, calculations, and integration
 */

const NormalizationIntegration = require('./normalizationIntegration');
const NormalizationCalculator = require('./normalization');
const DataParser = require('./dataParser');
const DatabaseManager = require('./database');

class NormalizationTester {
  constructor() {
    this.calculator = new NormalizationCalculator();
    this.parser = new DataParser();
    this.integration = new NormalizationIntegration();
    this.testResults = [];
  }

  // Test helper function
  addTestResult(testName, passed, details = '') {
    this.testResults.push({
      test: testName,
      passed,
      details,
      timestamp: new Date().toISOString()
    });
    
    const status = passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${status}: ${testName}${details ? ' - ' + details : ''}`);
  }

  // Test normalization calculations
  async testNormalizationCalculations() {
    console.log('\n🧮 Testing Normalization Calculations...');

    // Test RSI normalization
    const rsiTest1 = this.calculator.normalizeRSI(70);
    const rsiExpected1 = (70 - 50) / 50; // 0.4
    this.addTestResult(
      'RSI Normalization (70)',
      Math.abs(rsiTest1 - rsiExpected1) < 0.001,
      `Expected: ${rsiExpected1}, Got: ${rsiTest1}`
    );

    const rsiTest2 = this.calculator.normalizeRSI(30);
    const rsiExpected2 = (30 - 50) / 50; // -0.4
    this.addTestResult(
      'RSI Normalization (30)',
      Math.abs(rsiTest2 - rsiExpected2) < 0.001,
      `Expected: ${rsiExpected2}, Got: ${rsiTest2}`
    );

    // Test Williams %R normalization
    const williamsTest = this.calculator.normalizeWilliamsR(-20);
    const williamsExpected = (-20 + 50) / 50; // 0.6
    this.addTestResult(
      'Williams %R Normalization (-20)',
      Math.abs(williamsTest - williamsExpected) < 0.001,
      `Expected: ${williamsExpected}, Got: ${williamsTest}`
    );

    // Test MACD normalization
    const macdTest = this.calculator.normalizeMacd(2.5, 2.0);
    const macdExpected = (2.5 - 2.0) / Math.abs(2.0); // 0.25
    this.addTestResult(
      'MACD Normalization',
      Math.abs(macdTest - macdExpected) < 0.001,
      `Expected: ${macdExpected}, Got: ${macdTest}`
    );

    // Test Moving Average trend
    const maTrendTest = this.calculator.normalizeMovingAverageTrend(105, 100);
    const maTrendExpected = (105 - 100) / 100; // 0.05
    this.addTestResult(
      'MA Trend Normalization',
      Math.abs(maTrendTest - maTrendExpected) < 0.001,
      `Expected: ${maTrendExpected}, Got: ${maTrendTest}`
    );

    // Test ADX normalization
    const adxTest = this.calculator.normalizeADX(50);
    const adxExpected = (50 - 25) / 25; // 1.0
    this.addTestResult(
      'ADX Normalization',
      Math.abs(adxTest - adxExpected) < 0.001,
      `Expected: ${adxExpected}, Got: ${adxTest}`
    );

    // Test null handling
    const nullTest = this.calculator.normalizeRSI(null);
    this.addTestResult(
      'Null Value Handling',
      nullTest === null,
      `Expected: null, Got: ${nullTest}`
    );

    // Test composite score calculation
    const scores = [0.2, 0.4, -0.1, 0.3, null];
    const avgTest = this.calculator.calculateAverage(scores);
    const avgExpected = (0.2 + 0.4 - 0.1 + 0.3) / 4; // 0.2
    this.addTestResult(
      'Average Calculation with Nulls',
      Math.abs(avgTest - avgExpected) < 0.001,
      `Expected: ${avgExpected}, Got: ${avgTest}`
    );
  }

  // Test data parsing
  async testDataParsing() {
    console.log('\n📊 Testing Data Parsing...');

    // Create sample markdown table
    const sampleMarkdown = `
| Ticker | Company_Name | RSI_Value | RSI_Action | MACD_Value | MACD_Action |
|--------|--------------|-----------|------------|------------|-------------|
| AAPL | Apple Inc. | 65.2 | Buy | 1.5 | Buy |
| GOOGL | Alphabet Inc. | 45.8 | Sell | -0.8 | Sell |
| MSFT | Microsoft Corp. | N/A | Neutral | 0.2 | Neutral |
    `;

    const parseResult = this.parser.parseMarkdownTable(sampleMarkdown);
    
    this.addTestResult(
      'Markdown Table Parsing',
      parseResult.headers.length === 6 && parseResult.rows.length === 3,
      `Headers: ${parseResult.headers.length}, Rows: ${parseResult.rows.length}`
    );

    // Test row to KPI data conversion
    const kpiData = this.parser.rowToKpiData(
      parseResult.headers,
      parseResult.rows[0],
      '2025-09-26',
      '2025-09-26T00:00:00Z'
    );

    this.addTestResult(
      'Row to KPI Data Conversion',
      kpiData.ticker === 'AAPL' && kpiData.rsi_value === 65.2,
      `Ticker: ${kpiData.ticker}, RSI: ${kpiData.rsi_value}`
    );

    // Test validation
    const validation = this.parser.validateKpiData(kpiData);
    this.addTestResult(
      'KPI Data Validation',
      validation.isValid,
      `Valid: ${validation.isValid}, Errors: ${validation.errors.join(', ')}`
    );
  }

  // Test database operations
  async testDatabaseOperations() {
    console.log('\n🗄️ Testing Database Operations...');

    try {
      const db = new DatabaseManager();
      await db.initialize();

      // Test KPI data insertion
      const testKpiData = {
        ticker: 'TEST',
        company_name: 'Test Company',
        fetch_date: '2025-09-26',
        fetch_time: '2025-09-26T00:00:00Z',
        ti_summary: 'Buy',
        ti_buy_count: 8,
        ti_neutral_count: 1,
        ti_sell_count: 1,
        ma_summary: 'Strong Buy',
        ma_buy_count: 6,
        ma_sell_count: 0,
        rsi_value: 65.5,
        rsi_action: 'Buy',
        stochastic_value: 72.3,
        stochastic_action: 'Buy',
        macd_value: 1.2,
        macd_action: 'Buy',
        macd_signal: 1.0,
        adx_value: 35.0,
        adx_action: 'Buy',
        ma20_simple_value: 150.0,
        ma20_simple_action: 'Buy',
        ma50_simple_value: 145.0,
        ma50_simple_action: 'Buy',
        ma200_simple_value: 140.0,
        ma200_simple_action: 'Buy',
        current_price: 152.0,
        classic_pivot: 148.0,
        classic_r1: 155.0,
        classic_s1: 142.0
      };

      const kpiDataId = await db.insertKpiData(testKpiData);
      this.addTestResult(
        'KPI Data Insertion',
        kpiDataId > 0,
        `Inserted with ID: ${kpiDataId}`
      );

      // Test normalization calculation and insertion
      const normalizedData = this.calculator.normalizeKpiData(testKpiData);
      await db.insertNormalization(kpiDataId, normalizedData);

      this.addTestResult(
        'Normalization Data Insertion',
        true,
        'Successfully inserted normalized data'
      );

      // Test data retrieval
      const retrievedData = await db.getNormalizedData('TEST');
      this.addTestResult(
        'Data Retrieval',
        retrievedData.length > 0 && retrievedData[0].ticker === 'TEST',
        `Retrieved ${retrievedData.length} records`
      );

      // Test top performers query
      const topPerformers = await db.getTopPerformers(5);
      this.addTestResult(
        'Top Performers Query',
        Array.isArray(topPerformers),
        `Retrieved ${topPerformers.length} top performers`
      );

      db.close();

    } catch (error) {
      this.addTestResult(
        'Database Operations',
        false,
        `Error: ${error.message}`
      );
    }
  }

  // Test integration system
  async testIntegrationSystem() {
    console.log('\n🔗 Testing Integration System...');

    try {
      // Create mock Grok response
      const mockGrokResponse = {
        raw: `
| Ticker | Company_Name | RSI_Value | RSI_Action | MACD_Value | MACD_Action | MA20_Simple_Value | MA50_Simple_Value |
|--------|--------------|-----------|------------|------------|-------------|-------------------|-------------------|
| INTEG | Integration Test | 55.0 | Neutral | 0.5 | Buy | 100.0 | 98.0 |
        `,
        html: '<table>...</table>',
        fetchedAt: new Date().toISOString()
      };

      const result = await this.integration.processGrokResponse(mockGrokResponse, 10);
      
      this.addTestResult(
        'Integration Processing',
        result.processed > 0 && result.normalized > 0,
        `Processed: ${result.processed}, Normalized: ${result.normalized}`
      );

      // Test normalized data retrieval
      const normalizedData = await this.integration.getNormalizedData(['INTEG']);
      this.addTestResult(
        'Integration Data Retrieval',
        normalizedData.length > 0,
        `Retrieved ${normalizedData.length} normalized records`
      );

      // Test scores summary
      const summary = await this.integration.getScoresSummary();
      this.addTestResult(
        'Scores Summary',
        summary.summary && typeof summary.summary.totalRecords === 'number',
        `Total records: ${summary.summary.totalRecords}`
      );

    } catch (error) {
      this.addTestResult(
        'Integration System',
        false,
        `Error: ${error.message}`
      );
    }
  }

  // Test API endpoints
  async testApiEndpoints() {
    console.log('\n🌐 Testing API Endpoints...');

    const axios = require('axios');
    const baseUrl = 'http://localhost:3000/api/normalization';

    try {
      // Test health endpoint
      const healthResponse = await axios.get(`${baseUrl}/health`);
      this.addTestResult(
        'Health Endpoint',
        healthResponse.status === 200 && healthResponse.data.success,
        `Status: ${healthResponse.status}`
      );

      // Test stats endpoint
      const statsResponse = await axios.get(`${baseUrl}/stats`);
      this.addTestResult(
        'Stats Endpoint',
        statsResponse.status === 200 && statsResponse.data.success,
        `Total records: ${statsResponse.data.data.totalRecords}`
      );

      // Test top performers endpoint
      const topResponse = await axios.get(`${baseUrl}/top-performers?limit=5`);
      this.addTestResult(
        'Top Performers Endpoint',
        topResponse.status === 200 && topResponse.data.success,
        `Retrieved ${topResponse.data.count} performers`
      );

    } catch (error) {
      this.addTestResult(
        'API Endpoints',
        false,
        `Error: ${error.message}`
      );
    }
  }

  // Run all tests
  async runAllTests() {
    console.log('🚀 Starting Normalization System Tests...\n');

    await this.testNormalizationCalculations();
    await this.testDataParsing();
    await this.testDatabaseOperations();
    await this.testIntegrationSystem();
    
    // Only test API endpoints if server is running
    try {
      await this.testApiEndpoints();
    } catch (error) {
      console.log('⚠️ Skipping API tests (server not running)');
    }

    // Generate test report
    this.generateTestReport();
  }

  // Generate test report
  generateTestReport() {
    console.log('\n📋 Test Report Summary');
    console.log('========================');

    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.passed).length;
    const failedTests = totalTests - passedTests;

    console.log(`Total Tests: ${totalTests}`);
    console.log(`Passed: ${passedTests} ✅`);
    console.log(`Failed: ${failedTests} ❌`);
    console.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);

    if (failedTests > 0) {
      console.log('\n❌ Failed Tests:');
      this.testResults
        .filter(r => !r.passed)
        .forEach(r => console.log(`  - ${r.test}: ${r.details}`));
    }

    console.log('\n🎯 Test Categories:');
    const categories = {};
    this.testResults.forEach(r => {
      const category = r.test.split(' ')[0];
      if (!categories[category]) categories[category] = { passed: 0, total: 0 };
      categories[category].total++;
      if (r.passed) categories[category].passed++;
    });

    Object.entries(categories).forEach(([category, stats]) => {
      const rate = ((stats.passed / stats.total) * 100).toFixed(1);
      console.log(`  ${category}: ${stats.passed}/${stats.total} (${rate}%)`);
    });

    // Close integration system
    this.integration.close();

    return {
      totalTests,
      passedTests,
      failedTests,
      successRate: (passedTests / totalTests) * 100,
      results: this.testResults
    };
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  const tester = new NormalizationTester();
  tester.runAllTests().catch(console.error);
}

module.exports = NormalizationTester;
