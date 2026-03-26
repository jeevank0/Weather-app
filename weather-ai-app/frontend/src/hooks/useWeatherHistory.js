import { useEffect, useState } from 'react';
import { deleteWeatherRecord, fetchWeatherHistory, updateWeatherRecord } from '../services/weatherService';

export function useWeatherHistory() {
  const [records, setRecords] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadHistory() {
    setIsLoading(true);
    setError('');
    try {
      const data = await fetchWeatherHistory();
      setRecords(data);
    } catch (err) {
      setRecords([]);
      setError(err.message || 'Unable to load history.');
    } finally {
      setIsLoading(false);
    }
  }

  async function updateRecord(recordId, payload) {
    try {
      const updated = await updateWeatherRecord(recordId, payload);
      setRecords((prev) => prev.map((row) => (row.id === recordId ? updated : row)));
      return { ok: true, error: '' };
    } catch (err) {
      return { ok: false, error: err.message || 'Failed to update record.' };
    }
  }

  async function deleteRecord(recordId) {
    try {
      await deleteWeatherRecord(recordId);
      setRecords((prev) => prev.filter((row) => row.id !== recordId));
      return { ok: true, error: '' };
    } catch (err) {
      return { ok: false, error: err.message || 'Failed to delete record.' };
    }
  }

  useEffect(() => {
    let isMounted = true;

    (async () => {
      setIsLoading(true);
      setError('');
      try {
        const data = await fetchWeatherHistory();
        if (isMounted) setRecords(data);
      } catch (err) {
        if (isMounted) {
          setRecords([]);
          setError(err.message || 'Unable to load history.');
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    })();

    return () => {
      isMounted = false;
    };
  }, []);

  return {
    records,
    isLoading,
    error,
    loadHistory,
    updateRecord,
    deleteRecord,
  };
}
