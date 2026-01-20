import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './SignupScreen.css';

const SignupScreen = () => {
    const navigate = useNavigate();

    // Form State
    const [formData, setFormData] = useState({
        username: '',
        fullName: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: 'user'
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    // Prepare payload for Backend (maps camelCase to snake_case)
    const prepareBackendPayload = () => {
        return {
            username: formData.username,
            password: formData.password,
            email: formData.email,
            full_name: formData.fullName,
            role: formData.role
        };
    };

    const handleSignup = (e) => {
        e.preventDefault();

        if (formData.password !== formData.confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        const payload = prepareBackendPayload();

        // Simulate API call
        console.log("Payload JSON:", JSON.stringify(payload, null, 2));
        alert(`Account prepared for: ${formData.username}\nRole: ${formData.role}`);

        // Fix: Navigate is now used, so ESLint won't complain
        navigate('/');
    };

    return (
        <div className="signup-screen">
            <div className="signup-card">

                <div className="signup-header-section">
                    <h1 className="signup-title">Create Account</h1>
                    <p className="signup-subtitle">Join EMSIB system today</p>
                </div>

                <form onSubmit={handleSignup}>

                    <div className="form-group">
                        <label>I am a:</label>
                        <select
                            name="role"
                            className="signup-select"
                            value={formData.role}
                            onChange={handleChange}
                        >
                            <option value="user">Building User</option>
                            <option value="admin">Administrator</option>
                            <option value="maintenance">Maintenance Engineer</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            name="username"
                            className="signup-input"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Full Name</label>
                        <input
                            type="text"
                            name="fullName"
                            className="signup-input"
                            value={formData.fullName}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Email Address</label>
                        <input
                            type="email"
                            name="email"
                            className="signup-input"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            name="password"
                            className="signup-input"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Confirm Password</label>
                        <input
                            type="password"
                            name="confirmPassword"
                            className="signup-input"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" className="signup-btn">Create Account</button>
                </form>

                <div className="login-link">
                    Already have an account? <Link to="/">Log in</Link>
                </div>
            </div>
        </div>
    );
};

export default SignupScreen;