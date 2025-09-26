# Btock Technical Dashboard

This project hosts a simple Express.js application that calls the Grok chat completions API to build a comprehensive technical analysis dashboard. The request uses the Investing.com technical summary pages for more than 200 tickers and renders the Markdown table that Grok produces into an interactive HTML table.

## Environment variables

| Variable  | Description                                    |
|-----------|------------------------------------------------|
| `grok_key` | Grok API key (configured in Railway secrets). |
| `DATABASE_URL` | PostgreSQL connection string provided by Railway. |

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

4. Open [http://localhost:3000](http://localhost:3000) to view the dashboard. Use the **Refresh data** button to force a fresh Grok call and the **Download Full Matrix (Excel)** button to export the complete dataset for offline analysis.

### Database integration

- Add the `DATABASE_URL` connection string from Railway to your `.env` file when running locally. The server will automatically create a `stock_data` table (if it does not exist), clear it, and insert the most recent dataset each time Grok returns a new dashboard.
- If `DATABASE_URL` is not provided, the application will skip database writes and continue to operate using in-memory caching only.

## Deployment on Railway

The included `Procfile` instructs Railway to run `npm start`. Ensure the `grok_key` environment variable is defined in your Railway project settings. The application caches the Grok response for 30 minutes to minimize API calls while still allowing manual refreshes via the UI.
