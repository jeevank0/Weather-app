import { useState } from 'react';
import { Link } from 'react-router-dom';
import { exportWeatherData } from '../services/weatherService';
import HistoryTable from '../components/HistoryTable';
import { useWeatherHistory } from '../hooks/useWeatherHistory';

function HistoryPage() {
  const { records, isLoading, error, updateRecord, deleteRecord } = useWeatherHistory();
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState('');

  const handleExport = async (format) => {
    setIsExporting(true);
    setExportError('');
    try {
      const { blob, filename } = await exportWeatherData(format);
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(err.message || 'Unable to export history data.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <main className="page">
      <section className="container">
        <h2>History</h2>
        <p className="subtitle">Previously stored weather requests from the backend.</p>
        <div className="quick-nav" aria-label="Page navigation">
          <Link to="/" className="quick-nav-link">
            Back to Home
          </Link>
        </div>
        <div className="history-toolbar">
          <button type="button" className="export-btn" onClick={() => handleExport('csv')} disabled={isExporting}>
            {isExporting ? 'Exporting...' : 'Export CSV'}
          </button>
          <button type="button" className="export-btn" onClick={() => handleExport('json')} disabled={isExporting}>
            {isExporting ? 'Exporting...' : 'Export JSON'}
          </button>
        </div>
        {exportError && <p className="error">{exportError}</p>}
        {isLoading && <p className="muted">Loading history...</p>}
        {error && <p className="error">{error}</p>}
        {!isLoading && !error && (
          <HistoryTable records={records} onUpdate={updateRecord} onDelete={deleteRecord} />
        )}
      </section>
    </main>
  );
}

export default HistoryPage;
