const express = require('express');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const { marked } = require('marked');
const ExcelJS = require('exceljs');
const NormalizationIntegration = require('./normalizationIntegration');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const GROK_API_URL = 'https://api.x.ai/v1/chat/completions';
const CACHE_TTL_MS = 1000 * 60 * 30; // 30 minutes
const PROMPT_PATH = path.join(__dirname, 'prompts', 'full-request.txt');
const DATA_PATH = path.join(__dirname, 'prompts', 'url_tickers.csv');

let cachedPayloads = new Map(); // Use Map to cache different ticker limits separately
let cachedAt = 0;

// Initialize normalization system
const normalization = new NormalizationIntegration();

app.use(express.static(path.join(__dirname, 'public')));

// Initialize normalization routes
const { initializeRoutes } = require('./normalizationRoutes');
app.use('/api/normalization', initializeRoutes(normalization));

const sanitizeApiKey = (apiKey) => {
  if (!apiKey) {
    return '';
  }

  // Remove all control characters (including newlines, carriage returns and tabs)
  // as well as spaces, which are not allowed in HTTP header values.
  return String(apiKey)
    .trim()
    .replace(/[^\x21-\x7E]+/g, '');
};

const loadPrompt = (tickerLimit = null) => {
  const template = fs.readFileSync(PROMPT_PATH, 'utf-8');
  if (!template.trim()) {
    throw new Error('Prompt template is empty.');
  }

  const dataRaw = fs.readFileSync(DATA_PATH, 'utf-8').trim();
  if (!dataRaw) {
    throw new Error('Ticker dataset is empty.');
  }

  const [header, ...allRows] = dataRaw.split('\n');
  
  // Apply ticker limit if specified
  let rows = allRows;
  if (tickerLimit && tickerLimit !== 'all') {
    const limitValue = Number(tickerLimit);
    if (Number.isFinite(limitValue) && limitValue > 0) {
      rows = allRows.slice(0, limitValue);
    }
  }

  const sheetRows = rows
    .map((line, index) => `row${index + 2}: ${line}`)
    .join('\n\n');

  const document = `<DOCUMENT filename="URL.xlsx">\n<SHEET id="0" name="URL-Ticker">row1: ${header}\n\n${sheetRows}\n</SHEET></DOCUMENT>`;

  // Update the prompt to reflect the actual number of tickers being processed
  const tickerCount = rows.length;
  const endRow = tickerCount + 1; // +1 because we start from row 2
  let updatedTemplate = template.replace(
    /(there are over 200, starting from row 2 to row 213)/,
    `there are ${tickerCount}, starting from row 2 to row ${endRow}`
  );

  return updatedTemplate.replace('{{DOCUMENT}}', document);
};

const getConfiguredApiKey = () => {
  const apiKey = process.env.grok_key || process.env.GROK_KEY;
  if (!apiKey) {
    throw new Error('Grok API key is not configured. Please set the grok_key environment variable.');
  }

  const sanitizedApiKey = sanitizeApiKey(apiKey);
  if (!sanitizedApiKey) {
    throw new Error(
      'Grok API key is invalid. Ensure the grok_key environment variable only contains printable ASCII characters.'
    );
  }

  return sanitizedApiKey;
};

const requestDashboardFromGrok = async (tickerLimit = null) => {
  const prompt = loadPrompt(tickerLimit);
  const sanitizedApiKey = getConfiguredApiKey();

  const requestBody = {
    model: process.env.GROK_MODEL || 'grok-3',
    messages: [
      {
        role: 'user',
        content: prompt
      }
    ],
    temperature: 0.7,
    max_tokens: 8192,
    stream: false
  };

  const response = await axios.post(GROK_API_URL, requestBody, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${sanitizedApiKey}`
    },
    timeout: 1000 * 60 * 5
  });

  const content =
    response?.data?.choices?.[0]?.message?.content ||
    response?.data?.choices?.[0]?.text ||
    '';

  if (!content) {
    throw new Error('No content returned from Grok API');
  }

  const html = marked.parse(content);

  const payload = {
    raw: content,
    html,
    fetchedAt: new Date().toISOString()
  };

  // Cache the payload with the specific ticker limit
  const cacheKey = tickerLimit || 'all';
  cachedPayloads.set(cacheKey, payload);
  cachedAt = Date.now();

  return payload;
};

const getDashboardData = async ({ skipCache, tickerLimit } = {}) => {
  const cacheKey = tickerLimit || 'all';
  const cachedPayload = cachedPayloads.get(cacheKey);
  const cacheIsFresh = cachedPayload && Date.now() - cachedAt < CACHE_TTL_MS;
  
  if (!skipCache && cacheIsFresh) {
    return { payload: cachedPayload, cached: true };
  }

  const payload = await requestDashboardFromGrok(tickerLimit);
  
  // Process data through normalization system
  try {
    console.log('Processing data through normalization system...');
    const normalizationResult = await normalization.processGrokResponse(payload, tickerLimit);
    console.log(`Normalization completed: ${normalizationResult.normalized} records processed`);
    
    // Add normalization metadata to payload
    payload.normalization = normalizationResult;
  } catch (error) {
    console.error('Normalization processing failed:', error.message);
    // Continue without normalization if it fails
    payload.normalization = { error: error.message };
  }
  
  return { payload, cached: false };
};

const extractPlainText = (cell) => {
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
          return extractPlainText({ tokens: token.tokens || [], text: token.text });
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
};

const parseMarkdownTable = (markdown) => {
  if (!markdown) {
    return { headers: [], rows: [] };
  }

  const tokens = marked.lexer(markdown);
  const tableToken = tokens.find((token) => token.type === 'table' && token.header?.length);

  if (!tableToken) {
    return { headers: [], rows: [] };
  }

  const headers = tableToken.header.map((cell) => extractPlainText(cell));
  const rows = tableToken.rows.map((row) => row.map((cell) => extractPlainText(cell)));

  return { headers, rows };
};

const buildWorkbookFromTable = ({ headers, rows }) => {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Dashboard Matrix');

  worksheet.columns = headers.map((header, index) => ({
    header,
    key: `col${index}`,
    width: Math.min(Math.max(header.length + 2, 12), 40)
  }));

  rows.forEach((row) => {
    const normalizedRow = headers.map((_, index) => row[index] ?? '');
    worksheet.addRow(normalizedRow);
  });

  worksheet.getRow(1).font = { bold: true };

  worksheet.columns.forEach((column) => {
    let maxLength = column.header ? String(column.header).length : 10;
    column.eachCell({ includeEmpty: true }, (cell) => {
      const value = cell.value;
      if (value === null || value === undefined) {
        return;
      }
      const length = String(value).length;
      if (length > maxLength) {
        maxLength = length;
      }
    });
    column.width = Math.min(maxLength + 2, 48);
  });

  return workbook;
};

const normalizeTickerLimit = (value) => {
  if (value === undefined || value === null) {
    return null;
  }

  const normalized = String(value).trim();
  if (!normalized) {
    return null;
  }

  if (normalized.toLowerCase() === 'all') {
    return null;
  }

  const parsed = Number(normalized);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null;
  }

  return parsed;
};

app.get('/api/dashboard', async (req, res) => {
  try {
    const skipCache = String(req.query.refresh || 'false').toLowerCase() === 'true';
    const tickerLimit = normalizeTickerLimit(req.query.limit);
    const { payload, cached } = await getDashboardData({ skipCache, tickerLimit });
    return res.json({ ...payload, cached });
  } catch (error) {
    console.error('Error calling Grok API:', error?.response?.data || error.message || error);
    const status = error?.response?.status || 500;
    const message =
      error?.response?.data?.error?.message ||
      error?.message ||
      'Unexpected error calling Grok API';
    res.status(status).json({ error: message });
  }
});

app.get('/api/dashboard/export', async (req, res) => {
  try {
    const skipCache = String(req.query.refresh || 'false').toLowerCase() === 'true';
    const tickerLimit = normalizeTickerLimit(req.query.limit);
    // Use the same data source as the dashboard endpoint to ensure consistency
    const { payload } = await getDashboardData({ skipCache, tickerLimit });
    const table = parseMarkdownTable(payload.raw);

    if (!table.headers.length || !table.rows.length) {
      return res
        .status(500)
        .json({ error: 'Unable to parse dashboard matrix for export. Please try refreshing the data.' });
    }

    // No need to limit rows again since getDashboardData already applied the limit
    const workbook = buildWorkbookFromTable({ headers: table.headers, rows: table.rows });
    const snapshotDate = (() => {
      try {
        return new Date(payload.fetchedAt).toISOString().split('T')[0];
      } catch (_error) {
        return new Date().toISOString().split('T')[0];
      }
    })();

    res.setHeader(
      'Content-Disposition',
      `attachment; filename="btock-dashboard-matrix-${snapshotDate}.xlsx"`
    );
    res.setHeader(
      'Content-Type',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );

    await workbook.xlsx.write(res);
    res.end();
  } catch (error) {
    console.error('Error generating dashboard export:', error?.response?.data || error.message || error);
    const status = error?.response?.status || 500;
    const message =
      error?.response?.data?.error?.message ||
      error?.message ||
      'Unexpected error generating dashboard export';
    if (!res.headersSent) {
      res.status(status).json({ error: message });
    }
  }
});

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
