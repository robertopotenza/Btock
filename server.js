const express = require('express');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const { marked } = require('marked');
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

app.get('/api/dashboard', async (req, res) => {
  try {
    const skipCache = String(req.query.refresh || 'false').toLowerCase() === 'true';

    if (!skipCache && cachedPayload && Date.now() - cachedAt < CACHE_TTL_MS) {
      return res.json({ ...cachedPayload, cached: true });
    }

    const apiKey = process.env.grok_key || process.env.GROK_KEY;
    if (!apiKey) {
      return res.status(500).json({
        error: 'Grok API key is not configured. Please set the grok_key environment variable.'
      });
    }

    const sanitizedApiKey = sanitizeApiKey(apiKey);
    if (!sanitizedApiKey) {
      return res.status(500).json({
        error:
          'Grok API key is invalid. Ensure the grok_key environment variable only contains printable ASCII characters.'
      });
    }

    const prompt = loadPrompt();

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

    return res.json({ ...cachedPayload, cached: false });
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

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
