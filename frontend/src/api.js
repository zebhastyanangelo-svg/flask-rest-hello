const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

export async function signup(email, password) {
  const res = await fetch(`${API_URL}/api/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.msg || 'Signup failed');
  return data;
}

export async function login(email, password) {
  const res = await fetch(`${API_URL}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.msg || 'Login failed');
  return data;
}

export async function validateToken(token) {
  const res = await fetch(`${API_URL}/api/validate-token`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.msg || 'Token invalid');
  return data;
}

export async function getPrivateData(token) {
  const res = await fetch(`${API_URL}/api/private`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.msg || 'Access denied');
  return data;
}
