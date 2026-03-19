import { useState } from 'react';
import DataSubmissionForm from '../components/DataSubmissionForm.jsx';
import InsightsPanel from '../components/InsightsPanel.jsx';
import PluginManager from '../components/PluginManager.jsx';
import { useAuth } from '../context/AuthContext.jsx';

export default function DashboardPage() {
  const { auth, logout } = useAuth();
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <main className="page dashboard-page stack-lg">
      <section className="hero-banner">
        <div>
          <p className="eyebrow">Enterprise AI Operations</p>
          <h1>Welcome, {auth.user?.name}</h1>
          <p>
            Role: <strong>{auth.user?.role}</strong>
          </p>
        </div>
        <button type="button" onClick={logout}>Logout</button>
      </section>

      <div className="grid-two">
        <DataSubmissionForm token={auth.token} onSubmitted={() => setRefreshKey((current) => current + 1)} />
        <InsightsPanel token={auth.token} refreshKey={refreshKey} />
      </div>

      <PluginManager token={auth.token} role={auth.user?.role} />
    </main>
  );
}
