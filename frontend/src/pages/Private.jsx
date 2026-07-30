import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export default function Private() {
  const { user } = useAuth();

  return (
    <div className="page private-page">
      <h1>Private Dashboard</h1>
      <div className="card">
        <h2>Welcome, {user?.email}</h2>
        <p>This is a protected page. Only authenticated users can see this.</p>
        <p className="secret">🔒 Secret data: This is private content visible only to logged-in users.</p>
      </div>
      <Link to="/" className="btn">Back to Home</Link>
    </div>
  );
}
