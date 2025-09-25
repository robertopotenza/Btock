const statusEl = document.getElementById('status');
const contentEl = document.getElementById('content');
const refreshButton = document.getElementById('refreshButton');

const setStatus = (message, type = 'info') => {
  statusEl.innerHTML = `<p class="${type === 'error' ? 'error' : ''}">${message}</p>`;
};

const renderContent = ({ html, fetchedAt, cached }) => {
  const updatedAt = fetchedAt ? new Date(fetchedAt).toLocaleString() : 'Unknown';
  const cacheNote = cached ? ' (served from cache)' : '';

  contentEl.innerHTML = `
    <div class="table-wrapper">${html}</div>
    <p class="footer-note">Last updated: ${updatedAt}${cacheNote}</p>
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
    handleError(error);
  } finally {
    refreshButton.disabled = false;
  }
};

refreshButton.addEventListener('click', () => fetchData(true));

fetchData();
