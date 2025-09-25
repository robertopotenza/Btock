const statusEl = document.getElementById('status');
const contentEl = document.getElementById('content');
const refreshButton = document.getElementById('refreshButton');
const downloadButton = document.getElementById('downloadButton');

let latestSnapshotIso = null;

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

const renderContent = ({ html, fetchedAt, cached }) => {
  const safeHtml = enforceDynamicSnapshotDate(html, fetchedAt);
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

const fetchData = async (forceRefresh = false) => {
  setStatus('Fetching the latest Grok dashboard...');
  contentEl.innerHTML = '';
  refreshButton.disabled = true;
  downloadButton.disabled = true;
  let encounteredError = false;

  try {
    const query = forceRefresh ? '?refresh=true' : '';
    const response = await fetch(`/api/dashboard${query}`);
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.error || 'Unexpected error');
    }

    const data = await response.json();
    setStatus('Dashboard loaded successfully.');
    renderContent(data);
  } catch (error) {
    encounteredError = true;
    latestSnapshotIso = null;
    handleError(error);
  } finally {
    refreshButton.disabled = false;
    downloadButton.disabled = encounteredError || !latestSnapshotIso;
  }
};

refreshButton.addEventListener('click', () => fetchData(true));

downloadButton.addEventListener('click', async () => {
  const fallbackDate = new Date().toISOString().split('T')[0];
  const { dateLabel } = formatSnapshotDate(latestSnapshotIso);
  const timestamp = dateLabel === 'Unknown' ? fallbackDate : dateLabel;
  setStatus('Preparing the full dashboard matrix export...');
  downloadButton.disabled = true;

  try {
    const response = await fetch('/api/dashboard/export');
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
    setStatus('Full dashboard matrix downloaded successfully.');
  } catch (error) {
    console.error('Failed to download dashboard export:', error);
    setStatus('Unable to download the full dashboard matrix. Please try again shortly.', 'error');
  } finally {
    downloadButton.disabled = false;
  }
});

fetchData();
