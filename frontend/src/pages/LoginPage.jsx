import { Navigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm.jsx';
import { useAuth } from '../context/AuthContext.jsx';

export default function LoginPage() {
  const { auth } = useAuth();

  if (auth.token) {
    return <Navigate to="/" replace />;
  }

  return (
    <main className="page auth-page">
      <LoginForm />
    </main>
  );
}
