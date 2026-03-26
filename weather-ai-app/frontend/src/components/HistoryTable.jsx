import { useState } from 'react';
import { formatLocationName } from '../utils/locationFormat';

function HistoryTable({ records, onUpdate, onDelete }) {
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({
    location: '',
    start_date: '',
    end_date: '',
    temperature: '',
  });
  const [actionError, setActionError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const startEdit = (row) => {
    setEditingId(row.id);
    setActionError('');
    setForm({
      location: formatLocationName(row.location),
      start_date: row.start_date,
      end_date: row.end_date,
      temperature: String(row.temperature),
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setActionError('');
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const saveEdit = async () => {
    if (!editingId) return;
    setIsSubmitting(true);
    setActionError('');

    const payload = {
      location: form.location.trim(),
      start_date: form.start_date,
      end_date: form.end_date,
      temperature: Number(form.temperature),
    };
    const result = await onUpdate(editingId, payload);

    setIsSubmitting(false);
    if (!result.ok) {
      setActionError(result.error);
      return;
    }

    setEditingId(null);
  };

  const removeRow = async (id) => {
    setActionError('');
    setIsSubmitting(true);
    const result = await onDelete(id);
    setIsSubmitting(false);
    if (!result.ok) {
      setActionError(result.error);
    }
  };

  if (!records.length) {
    return <p className="empty-state">No records found.</p>;
  }

  return (
    <div>
      {actionError && <p className="error">{actionError}</p>}
      <div className="table-wrap">
        <table>
        <thead>
          <tr>
            <th>Location</th>
            <th>Start Date</th>
            <th>End Date</th>
            <th>Temperature</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {records.map((row) => (
            <tr key={row.id}>
              <td>
                {editingId === row.id ? (
                  <input name="location" value={form.location} onChange={handleInputChange} className="table-input" />
                ) : (
                  formatLocationName(row.location)
                )}
              </td>
              <td>
                {editingId === row.id ? (
                  <input
                    type="date"
                    name="start_date"
                    value={form.start_date}
                    onChange={handleInputChange}
                    className="table-input"
                  />
                ) : (
                  row.start_date
                )}
              </td>
              <td>
                {editingId === row.id ? (
                  <input
                    type="date"
                    name="end_date"
                    value={form.end_date}
                    onChange={handleInputChange}
                    className="table-input"
                  />
                ) : (
                  row.end_date
                )}
              </td>
              <td>
                {editingId === row.id ? (
                  <input
                    type="number"
                    step="0.1"
                    name="temperature"
                    value={form.temperature}
                    onChange={handleInputChange}
                    className="table-input"
                  />
                ) : (
                  `${Number(row.temperature).toFixed(1)}°C`
                )}
              </td>
              <td>{new Date(row.created_at).toLocaleString()}</td>
              <td>
                <div className="table-actions">
                  {editingId === row.id ? (
                    <>
                      <button type="button" className="action-btn save" onClick={saveEdit} disabled={isSubmitting}>
                        Save
                      </button>
                      <button type="button" className="action-btn" onClick={cancelEdit} disabled={isSubmitting}>
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button type="button" className="action-btn" onClick={() => startEdit(row)} disabled={isSubmitting}>
                        Edit
                      </button>
                      <button
                        type="button"
                        className="action-btn delete"
                        onClick={() => removeRow(row.id)}
                        disabled={isSubmitting}
                      >
                        Delete
                      </button>
                    </>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
        </table>
      </div>
    </div>
  );
}

export default HistoryTable;
