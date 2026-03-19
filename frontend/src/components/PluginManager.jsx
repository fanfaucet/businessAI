import { useEffect, useState } from 'react';
import { apiRequest } from '../api/client.js';

export default function PluginManager({ token, role }) {
  const [plugins, setPlugins] = useState({ available: [], active: [] });
  const [error, setError] = useState('');

  const loadPlugins = async () => {
    try {
      const response = await apiRequest('/plugins', { token });
      setPlugins(response);
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  useEffect(() => {
    loadPlugins();
  }, []);

  const activatePlugin = async (key) => {
    try {
      await apiRequest('/plugins/load', {
        method: 'POST',
        token,
        body: { key, config: { activatedFromUi: true } },
      });
      await loadPlugins();
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Plugin manager</h2>
        <p>Enable modular intelligence utilities for workflow-specific analysis.</p>
      </div>
      {error && <div className="error-banner">{error}</div>}
      <div className="grid-two">
        <div>
          <h3>Available plugins</h3>
          {plugins.available.map((plugin) => (
            <div key={plugin.key} className="plugin-card">
              <strong>{plugin.name}</strong>
              <p>{plugin.description}</p>
              <button type="button" disabled={!['admin', 'analyst'].includes(role)} onClick={() => activatePlugin(plugin.key)}>
                Load plugin
              </button>
            </div>
          ))}
        </div>
        <div>
          <h3>Active plugins</h3>
          {plugins.active.length === 0 ? (
            <p>No active plugins yet.</p>
          ) : (
            plugins.active.map((plugin) => (
              <div key={plugin.id} className="plugin-card">
                <strong>{plugin.name}</strong>
                <pre>{JSON.stringify(plugin.config, null, 2)}</pre>
              </div>
            ))
          )}
        </div>
      </div>
      {!['admin', 'analyst'].includes(role) && <small>Plugin activation is restricted to admin and analyst roles.</small>}
    </section>
  );
}
