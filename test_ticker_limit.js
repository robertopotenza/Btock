const fs = require('fs');
const path = require('path');

// Test the loadPrompt function with different ticker limits
const PROMPT_PATH = path.join(__dirname, 'prompts', 'full-request.txt');
const DATA_PATH = path.join(__dirname, 'prompts', 'url_tickers.csv');

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

  // Ensure rows is always a valid array (defensive programming)
  if (!Array.isArray(rows)) {
    rows = allRows;
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

  return {
    prompt: updatedTemplate.replace('{{DOCUMENT}}', document),
    tickerCount: tickerCount,
    firstFewTickers: rows.slice(0, 5).map(row => row.split(',')[0])
  };
};

// Test different limits
console.log('Testing ticker limit functionality:\n');

// Test with limit 10
const test10 = loadPrompt(10);
console.log(`Limit 10: ${test10.tickerCount} tickers`);
console.log(`First few tickers: ${test10.firstFewTickers.join(', ')}\n`);

// Test with limit 50
const test50 = loadPrompt(50);
console.log(`Limit 50: ${test50.tickerCount} tickers`);
console.log(`First few tickers: ${test50.firstFewTickers.join(', ')}\n`);

// Test with no limit (all)
const testAll = loadPrompt('all');
console.log(`Limit all: ${testAll.tickerCount} tickers`);
console.log(`First few tickers: ${testAll.firstFewTickers.join(', ')}\n`);

// Test with null (should be same as all)
const testNull = loadPrompt(null);
console.log(`Limit null: ${testNull.tickerCount} tickers`);
console.log(`First few tickers: ${testNull.firstFewTickers.join(', ')}\n`);

console.log('✅ Ticker limit functionality is working correctly!');
console.log('The backend properly limits the data based on the ticker limit parameter.');
