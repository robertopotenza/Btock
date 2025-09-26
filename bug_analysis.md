# Bug Analysis: Ticker Count Selection Not Respected

## Current Implementation Issues

### 1. Frontend Behavior
- User selects "First 10", "First 50", or "All" from dropdown
- Frontend calls `/api/dashboard` without passing the selection
- Frontend receives full dataset for all 212 tickers
- Frontend then hides excess rows using JavaScript (`applyTickerLimit` function)
- This is inefficient and doesn't solve the core problem

### 2. Backend Behavior
- `/api/dashboard` endpoint ignores user selection
- Always loads full prompt with all 212 tickers
- Sends complete dataset to Grok API regardless of user needs
- Wastes API calls and processing time

### 3. Export Issue
- Excel export does accept a `limit` parameter
- But it only truncates the already-fetched full dataset
- Still processes all tickers through Grok API first

## Root Cause
The `loadPrompt()` function in `server.js` always includes all tickers from the CSV file in the document sent to Grok API. The prompt template asks Grok to process "each ticker in the list (there are over 200, starting from row 2 to row 213)".

## Proposed Solution

### 1. Modify Frontend
- Pass `limit` parameter to `/api/dashboard` endpoint
- Remove client-side row hiding logic since backend will return correct data

### 2. Modify Backend
- Accept `limit` parameter in `/api/dashboard` endpoint
- Modify `loadPrompt()` function to accept a limit parameter
- Dynamically construct the document with only the requested number of tickers
- Update the prompt text to reflect the actual number of tickers being processed

### 3. Benefits
- Reduces Grok API processing time and costs
- Improves response times for smaller datasets
- Makes the "Download Full Matrix" feature truly respect user selection
- Eliminates unnecessary data transfer

## Files to Modify
1. `/public/app.js` - Update API calls to include limit parameter
2. `/server.js` - Modify endpoints and prompt loading logic
3. `/prompts/full-request.txt` - Make ticker count dynamic (optional)

## Implementation Details
- The CSV has 213 lines total (1 header + 212 data rows)
- When limit is "10", include rows 2-11 from CSV
- When limit is "50", include rows 2-51 from CSV  
- When limit is "all", include rows 2-213 from CSV
- Update prompt text to reflect actual ticker count being processed
