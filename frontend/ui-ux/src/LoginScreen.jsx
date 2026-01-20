import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import './LoginScreen.css';

const LoginScreen = () => {
    const navigate = useNavigate();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    // Stany UI
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const handleLogin = (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        setTimeout(() => {
            // Logowanie po USERNAME (zgodnie z backendem)
            if (username === 'admin' && password === '1234') {
                localStorage.setItem('userRole', 'admin');
                navigate('/admin');
            }
            else if (username === 'user' && password === '1234') {
                localStorage.setItem('userRole', 'user');
                navigate('/user');
            }
            else {
                setError('Invalid username or password. Try: admin / 1234');
            }
            setIsLoading(false);
        }, 1500);
    };

    return (
        <div className="login-screen">
            <div className="login-card">

                {/* Logo przeniesione do środka karty */}
                <div className="logo-section">
                    <div className="logo-circle">A</div>
                </div>

                <h1 className="login-title">Welcome Back</h1>
                <p className="login-subtitle">Sign in to your EMSIB account</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleLogin}>
                    <div className="input-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            type="text"
                            className="login-input"
                            placeholder="Enter username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label htmlFor="password">Password</label>
                        <div style={{ position: 'relative' }}>
                            <input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                className="login-input"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                style={{ paddingRight: '45px' }}
                            />
                            <span
                                onClick={() => setShowPassword(!showPassword)}
                                style={{
                                    position: 'absolute',
                                    right: '15px',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    cursor: 'pointer',
                                    color: '#64748b',
                                    fontSize: '1.2rem'
                                }}
                            >
                                {showPassword ? <FaEyeSlash /> : <FaEye />}
                            </span>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="login-button"
                        disabled={isLoading}
                    >
                        {isLoading ? 'Signing in...' : 'Log in'}
                    </button>
                </form>

                <div className="login-footer">
                    <a href="#forgot" style={{color: '#64748b', fontWeight: '400', fontSize: '0.85rem'}}>Forgot Password?</a>
                    <div style={{marginTop: '10px'}}>
                        Don't have an account? <Link to="/signup">Sign up</Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginScreen;