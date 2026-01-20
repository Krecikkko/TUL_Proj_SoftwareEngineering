// src/components/LoginScreen.jsx
import { useState } from 'react';
import { loginUser } from '../dv/facade/dvFacade';

export function LoginScreen({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // 1. Wołamy Twoją fasadę
    const result = await loginUser(username, password);

    if (result.status === 'ok') {
      // 2. Sukces! Informujemy App.jsx, że można wpuścić użytkownika
      onLoginSuccess();
    } else {
      setError(result.message);
    }
  };

  return (
    <div style={{ maxWidth: 300, margin: "50px auto", padding: 20, border: "1px solid #ccc" }}>
      <h2>Please Log In</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <input 
          type="text" 
          placeholder="Username" 
          value={username} 
          onChange={e => setUsername(e.target.value)} 
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={e => setPassword(e.target.value)} 
        />
        <button type="submit">Log In</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}