const statusEl = document.getElementById('status');
const contentEl = document.getElementById('content');
const refreshButton = document.getElementById('refreshButton');
const downloadButton = document.getElementById('downloadButton');
const tickerLimitInput = document.getElementById('tickerLimit');

let latestSnapshotIso = null;
let currentLimit = null;

const describeLimit = (limit) => {
  if (limit === 'all') {
    return 'all available tickers';
  }

  const parsed = Number(limit);
  if (Number.isFinite(parsed) && parsed > 0) {
    return `the first ${parsed} tickers`;
  }

  return 'the selected tickers';
};

const formatSnapshotDate = (isoString) => {
  if (!isoString) {
    return { dateLabel: 'Unknown', timeLabel: 'Unknown time' };
  }

  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return { dateLabel: 'Unknown', timeLabel: 'Unknown time' };
  }

  return {
    dateLabel: date.toISOString().split('T')[0],
    timeLabel: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  };
};

const enforceDynamicSnapshotDate = (html, fetchedAt) => {
  if (!html || !fetchedAt) {
    return html;
  }

  try {
    const { dateLabel } = formatSnapshotDate(fetchedAt);
    const template = document.createElement('template');
    template.innerHTML = html;
    const walker = document.createTreeWalker(template.content, NodeFilter.SHOW_TEXT);
    const pattern = /(Data\s+as\s+of\s+)(.+)/i;

    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!node?.textContent) {
        continue;
      }

      const match = node.textContent.match(pattern);
      if (match) {
        node.textContent = `${match[1]}${dateLabel}`;
        break;
      }
    }

    return template.innerHTML;
  } catch (_error) {
    return html;
  }
};

const setStatus = (message, type = 'info') => {
  statusEl.innerHTML = `<p class="${type === 'error' ? 'error' : ''}">${message}</p>`;
};

// applyTickerLimit function removed - backend now returns correctly sized data

const renderContent = ({ html, fetchedAt, cached }, limit) => {
  const safeHtml = enforceDynamicSnapshotDate(html, fetchedAt);
  // No need to apply client-side ticker limit since backend returns correct data
  const { dateLabel, timeLabel } = formatSnapshotDate(fetchedAt);
  const cacheNote = cached ? ' (served from cache)' : '';

  latestSnapshotIso = fetchedAt || null;

  contentEl.innerHTML = `
    <div class="table-wrapper">${safeHtml}</div>
    <p class="footer-note">Data snapshot date: ${dateLabel} &mdash; ${timeLabel} local time${cacheNote}</p>
  `;
};

const handleError = (error) => {
  console.error('Failed to load dashboard data:', error);
  setStatus('Unable to load dashboard data. Please try again shortly.', 'error');
  contentEl.innerHTML = '';
};

const fetchData = async ({ forceRefresh = false, limit } = {}) => {
  if (!limit) {
    return;
  }

  const limitDescription = describeLimit(limit);

  setStatus(`Fetching the latest Grok dashboard for ${limitDescription}...`);
  contentEl.innerHTML = '';
  refreshButton.disabled = true;
  downloadButton.disabled = true;
  tickerLimitInput.disabled = true;
  let encounteredError = false;

  try {
    const queryParams = new URLSearchParams();
    if (forceRefresh) {
      queryParams.set('refresh', 'true');
    }
    // Pass the limit parameter to the backend API
    if (limit) {
      queryParams.set('limit', limit);
    }

    const query = queryParams.toString();
    const response = await fetch(`/api/dashboard${query ? `?${query}` : ''}`);
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.error || 'Unexpected error');
    }

    const data = await response.json();
    setStatus(`Dashboard loaded successfully for ${limitDescription}.`);
    renderContent(data, limit);
  } catch (error) {
    encounteredError = true;
    latestSnapshotIso = null;
    handleError(error);
  } finally {
    refreshButton.disabled = !currentLimit;
    downloadButton.disabled = encounteredError || !latestSnapshotIso;
    tickerLimitInput.disabled = false;
  }
};

refreshButton.addEventListener('click', () => {
  if (!currentLimit) {
    setStatus('Please select how many tickers to display before refreshing.');
    return;
  }

  fetchData({ forceRefresh: true, limit: currentLimit });
});

tickerLimitInput.addEventListener('change', (event) => {
  const { value } = event.target;
  if (!value) {
    return;
  }

  currentLimit = value;
  fetchData({ limit: currentLimit });
});

downloadButton.addEventListener('click', async () => {
  if (!currentLimit) {
    setStatus('Please select how many tickers to include before downloading the matrix.');
    return;
  }

  const fallbackDate = new Date().toISOString().split('T')[0];
  const { dateLabel } = formatSnapshotDate(latestSnapshotIso);
  const timestamp = dateLabel === 'Unknown' ? fallbackDate : dateLabel;
  const limitDescription = describeLimit(currentLimit);
  setStatus(`Preparing the dashboard matrix export for ${limitDescription}...`);
  downloadButton.disabled = true;

  try {
    const queryParams = new URLSearchParams();
    if (currentLimit) {
      queryParams.set('limit', currentLimit);
    }

    const query = queryParams.toString();
    const response = await fetch(`/api/dashboard/export${query ? `?${query}` : ''}`);
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.error || 'Unexpected error');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `btock-dashboard-matrix-${timestamp}.xlsx`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.URL.revokeObjectURL(url);
    setStatus(`Dashboard matrix downloaded successfully for ${limitDescription}.`);
  } catch (error) {
    console.error('Failed to download dashboard export:', error);
    setStatus('Unable to download the full dashboard matrix. Please try again shortly.', 'error');
  } finally {
    downloadButton.disabled = false;
  }
});
