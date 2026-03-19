import { useState } from 'react';
import { apiRequest } from '../api/client.js';

const defaultPayload = `{
  "revenue": 120000,
  "expenses": 83000,
  "activeClients": 145,
  "churnRate": 4.2,
  "satisfactionScore": 8.9,
  "notes": "Q2 expansion across healthcare and logistics accounts."
}`;

export default function DataSubmissionForm({ token, onSubmitted }) {
  const [jsonPayload, setJsonPayload] = useState(defaultPayload);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setMessage('');

    try {
      const parsedPayload = JSON.parse(jsonPayload);
      await apiRequest('/data/submit', {
        method: 'POST',
        token,
        body: { jsonPayload: parsedPayload },
      });
      setMessage('Business data submitted successfully.');
      onSubmitted();
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Business data submission</h2>
        <p>Send structured operational metrics into the insight pipeline.</p>
      </div>
      <form onSubmit={handleSubmit} className="stack-md">
        <label>
          JSON payload
          <textarea rows="12" value={jsonPayload} onChange={(event) => setJsonPayload(event.target.value)} />
        </label>
        {message && <div className="success-banner">{message}</div>}
        {error && <div className="error-banner">{error}</div>}
        <button type="submit">Submit data</button>
      </form>
    </section>
  );
}
