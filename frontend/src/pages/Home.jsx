import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="page home-page">
      <h1>Welcome to MyApp</h1>
      <p>This is a public landing page.</p>
      {user ? (
        <Link to="/private" className="btn">Go to Dashboard</Link>
      ) : (
        <div className="home-actions">
          <Link to="/login" className="btn">Login</Link>
          <Link to="/signup" className="btn btn-secondary">Sign Up</Link>
        </div>
      )}
    </div>
  );
}
