import { useState } from 'react';
import { apiRequest } from '../api/client.js';

export default function InsightsPanel({ token, refreshKey }) {
  const [insight, setInsight] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchInsight = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await apiRequest('/insights/ai', { token });
      setInsight(response.insight);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel">
      <div className="panel-header inline-between">
        <div>
          <h2>AI insights</h2>
          <p>Generate strategic commentary from the latest submitted data.</p>
        </div>
        <button type="button" onClick={fetchInsight} disabled={loading}>
          {loading ? 'Generating...' : 'Generate insights'}
        </button>
      </div>
      {error && <div className="error-banner">{error}</div>}
      {insight ? (
        <div className="stack-sm">
          <article className="insight-card">
            <h3>Latest insight</h3>
            <p>{insight.insightText}</p>
          </article>
          <div>
            <h3>Plugin output</h3>
            <pre>{JSON.stringify(insight.pluginOutputs, null, 2)}</pre>
          </div>
          <small>Refresh key: {refreshKey}</small>
        </div>
      ) : (
        <p>No insights generated yet.</p>
      )}
    </section>
  );
}
