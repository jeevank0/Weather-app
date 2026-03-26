function AIInsights({ insights }) {
  const safeInsights = Array.isArray(insights)
    ? insights.filter((item) => item && typeof item.message === 'string' && item.message.trim())
    : [];

  if (!safeInsights.length) return null;

  return (
    <section className="insights-wrap panel-card" aria-live="polite">
      <h4>Weather Recommendations</h4>
      <ul className="insights-list">
        {safeInsights.map((insight, index) => (
          <li key={`${insight.type}-${index}`} className={`insight-card insight-${insight.type}`}>
            <p>{insight.message}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default AIInsights;
