const express = require('express');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const { marked } = require('marked');
const ExcelJS = require('exceljs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const GROK_API_URL = 'https://api.x.ai/v1/chat/completions';
const CACHE_TTL_MS = 1000 * 60 * 30; // 30 minutes
const PROMPT_PATH = path.join(__dirname, 'prompts', 'full-request.txt');
const DATA_PATH = path.join(__dirname, 'prompts', 'url_tickers.csv');

let cachedPayload = null;
let cachedAt = 0;

app.use(express.static(path.join(__dirname, 'public')));

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

const loadPrompt = () => {
  const template = fs.readFileSync(PROMPT_PATH, 'utf-8');
  if (!template.trim()) {
    throw new Error('Prompt template is empty.');
  }

  const dataRaw = fs.readFileSync(DATA_PATH, 'utf-8').trim();
  if (!dataRaw) {
    throw new Error('Ticker dataset is empty.');
  }

  const [, ...rows] = dataRaw.split('\n');
  const sheetRows = rows
    .map((line, index) => `row${index + 2}: ${line}`)
    .join('\n\n');

  const document = `<DOCUMENT filename="URL.xlsx">\n<SHEET id="0" name="URL-Ticker">row1: Ticker,URL,Company Name\n\n${sheetRows}\n</SHEET></DOCUMENT>`;

  return template.replace('{{DOCUMENT}}', document);
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

const requestDashboardFromGrok = async () => {
  const prompt = loadPrompt();
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

  cachedPayload = {
    raw: content,
    html,
    fetchedAt: new Date().toISOString()
  };
  cachedAt = Date.now();

  return cachedPayload;
};

const getDashboardData = async ({ skipCache } = {}) => {
  const cacheIsFresh = cachedPayload && Date.now() - cachedAt < CACHE_TTL_MS;
  if (!skipCache && cacheIsFresh) {
    return { payload: cachedPayload, cached: true };
  }

  const payload = await requestDashboardFromGrok();
  return { payload, cached: false };
};

const parseMarkdownTable = (markdown) => {
  if (!markdown) {
    return { headers: [], rows: [] };
  }

  const lines = markdown.split(/\r?\n/);
  const tableLines = [];
  let collecting = false;

  for (const line of lines) {
    if (/^\s*\|/.test(line)) {
      tableLines.push(line.trim());
      collecting = true;
      continue;
    }

    if (collecting) {
      const trimmed = line.trim();
      if (!trimmed) {
        break;
      }

      // If we encounter another section (e.g., markdown paragraph), stop collecting.
      if (!/^\s*\|/.test(line)) {
        break;
      }
    }
  }

  if (tableLines.length < 2) {
    return { headers: [], rows: [] };
  }

  const [headerLine, ...rest] = tableLines;
  const headers = headerLine
    .split('|')
    .slice(1, -1)
    .map((cell) => cell.trim());

  const rows = rest
    .filter((line) => !/^\|?\s*[:-]+/.test(line.replace(/\s+/g, '')))
    .map((line) =>
      line
        .split('|')
        .slice(1, -1)
        .map((cell) => cell.trim())
    )
    .filter((row) => row.length === headers.length);

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

app.get('/api/dashboard', async (req, res) => {
  try {
    const skipCache = String(req.query.refresh || 'false').toLowerCase() === 'true';
    const { payload, cached } = await getDashboardData({ skipCache });
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
    const { payload } = await getDashboardData({ skipCache });
    const table = parseMarkdownTable(payload.raw);

    if (!table.headers.length || !table.rows.length) {
      return res
        .status(500)
        .json({ error: 'Unable to parse dashboard matrix for export. Please try refreshing the data.' });
    }

    const workbook = buildWorkbookFromTable(table);
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
