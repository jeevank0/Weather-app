function LoadingSpinner({ label = 'Loading weather...' }) {
  return (
    <div className="loading-wrap" role="status" aria-live="polite" aria-label={label}>
      <span className="spinner" aria-hidden="true" />
      <span className="muted">{label}</span>
    </div>
  );
}

export default LoadingSpinner;
