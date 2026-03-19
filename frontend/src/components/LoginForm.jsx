import { useState } from 'react';
import { apiRequest } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

const initialState = {
  name: '',
  email: '',
  password: '',
  role: 'business_user',
};

export default function LoginForm() {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState(initialState);
  const [error, setError] = useState('');
  const { updateAuth } = useAuth();

  const submit = async (event) => {
    event.preventDefault();
    setError('');

    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/signup';
      const payload = mode === 'login'
        ? { email: form.email, password: form.password }
        : form;
      const response = await apiRequest(endpoint, { method: 'POST', body: payload });
      updateAuth(response);
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return (
    <div className="panel auth-panel">
      <div className="panel-header">
        <h1>AnnabanAI Business Suite</h1>
        <p>Secure access for enterprise automation teams.</p>
      </div>
      <form onSubmit={submit} className="stack-md">
        {mode === 'signup' && (
          <>
            <label>
              Name
              <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
            </label>
            <label>
              Role
              <select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value })}>
                <option value="business_user">Business User</option>
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
            </label>
          </>
        )}
        <label>
          Email
          <input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
        </label>
        <label>
          Password
          <input type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required />
        </label>
        {error && <div className="error-banner">{error}</div>}
        <button type="submit">{mode === 'login' ? 'Login' : 'Create account'}</button>
      </form>
      <button className="link-button" type="button" onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}>
        {mode === 'login' ? 'Need an account? Sign up' : 'Already have an account? Login'}
      </button>
    </div>
  );
}
