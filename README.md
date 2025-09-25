# Btock Technical Dashboard

This project hosts a simple Express.js application that calls the Grok chat completions API to build a comprehensive technical analysis dashboard. The request uses the Investing.com technical summary pages for more than 200 tickers and renders the Markdown table that Grok produces into an interactive HTML table.

## Environment variables

| Variable  | Description                                    |
|-----------|------------------------------------------------|
| `grok_key` | Grok API key (configured in Railway secrets). |

## Local development

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create a `.env` file (or export the variable) with your Grok API key:

   ```bash
   echo "grok_key=YOUR_KEY" > .env
   ```

3. Start the server:

   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view the dashboard. Use the **Refresh data** button to force a fresh Grok call.

## Deployment on Railway

The included `Procfile` instructs Railway to run `npm start`. Ensure the `grok_key` environment variable is defined in your Railway project settings. The application caches the Grok response for 30 minutes to minimize API calls while still allowing manual refreshes via the UI.
