import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './SignupScreen.css';

const SignupScreen = () => {
    const navigate = useNavigate();

    // STAN BEZ ZMIAN
    const [formData, setFormData] = useState({
        fullName: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: '',
        role: 'user',
        buildingName: '',
        companyCode: '',
        specialization: '',
        roomNumber: '',
        supplierName: '',
        contractNumber: '',
        technicianId: '',
        serviceRegion: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleSignup = (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            alert("Hasła nie są identyczne!");
            return;
        }
        console.log("Rejestracja - Actor:", formData.role, "Data:", formData);
        localStorage.setItem('userRole', formData.role);
        localStorage.setItem('userName', formData.fullName);
        alert(`Konto utworzone dla roli: ${formData.role.toUpperCase()}`);
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

                    {/* ROLA */}
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
                            <option value="supplier">Energy Supplier</option>
                            <option value="service">System Service</option>
                        </select>
                    </div>

                    {/* DANE OSOBOWE */}
                    <div className="form-group">
                        <label>Full Name</label>
                        <input type="text" name="fullName" className="signup-input" value={formData.fullName} onChange={handleChange} required />
                    </div>

                    <div className="form-group">
                        <label>Email Address</label>
                        <input type="email" name="email" className="signup-input" value={formData.email} onChange={handleChange} required />
                    </div>

                    <div className="form-group">
                        <label>Phone Number</label>
                        <input type="tel" name="phone" className="signup-input" value={formData.phone} onChange={handleChange} required />
                    </div>

                    {/* --- SEKCJE SPECYFICZNE DLA RÓL (W KONTENERACH) --- */}

                    {/* 1. ADMIN */}
                    {formData.role === 'admin' && (
                        <div className="role-specific-box">
                            <span className="role-specific-label">Admin Details</span>
                            <div className="form-group">
                                <label>Building Name</label>
                                <input type="text" name="buildingName" className="signup-input" placeholder="e.g. Sky Tower" value={formData.buildingName} onChange={handleChange} />
                            </div>
                            <div className="form-group">
                                <label>Company ID</label>
                                <input type="text" name="companyCode" className="signup-input" value={formData.companyCode} onChange={handleChange} />
                            </div>
                        </div>
                    )}

                    {/* 2. INŻYNIER */}
                    {formData.role === 'maintenance' && (
                        <div className="role-specific-box">
                            <span className="role-specific-label">Engineer Details</span>
                            <div className="form-group">
                                <label>Specialization</label>
                                <select name="specialization" className="signup-select" value={formData.specialization} onChange={handleChange}>
                                    <option value="">Select...</option>
                                    <option value="hvac">HVAC</option>
                                    <option value="electrical">Electrical</option>
                                    <option value="it">IT/Sensors</option>
                                </select>
                            </div>
                        </div>
                    )}

                    {/* 3. USER */}
                    {formData.role === 'user' && (
                        <div className="role-specific-box">
                            <span className="role-specific-label">Location</span>
                            <div className="form-group">
                                <label>Room Number</label>
                                <input type="text" name="roomNumber" className="signup-input" placeholder="e.g. 101" value={formData.roomNumber} onChange={handleChange} />
                            </div>
                        </div>
                    )}

                    {/* 4. SUPPLIER */}
                    {formData.role === 'supplier' && (
                        <div className="role-specific-box">
                            <span className="role-specific-label">Supplier Data</span>
                            <div className="form-group">
                                <label>Company Name</label>
                                <input type="text" name="supplierName" className="signup-input" value={formData.supplierName} onChange={handleChange} />
                            </div>
                            <div className="form-group">
                                <label>Contract ID</label>
                                <input type="text" name="contractNumber" className="signup-input" value={formData.contractNumber} onChange={handleChange} />
                            </div>
                        </div>
                    )}

                    {/* 5. SERVICE */}
                    {formData.role === 'service' && (
                        <div className="role-specific-box">
                            <span className="role-specific-label">Service Data</span>
                            <div className="form-group">
                                <label>Technician ID</label>
                                <input type="text" name="technicianId" className="signup-input" value={formData.technicianId} onChange={handleChange} />
                            </div>
                            <div className="form-group">
                                <label>Region</label>
                                <input type="text" name="serviceRegion" className="signup-input" value={formData.serviceRegion} onChange={handleChange} />
                            </div>
                        </div>
                    )}

                    <div className="form-group">
                        <label>Password</label>
                        <input type="password" name="password" className="signup-input" value={formData.password} onChange={handleChange} required />
                    </div>

                    <div className="form-group">
                        <label>Confirm Password</label>
                        <input type="password" name="confirmPassword" className="signup-input" value={formData.confirmPassword} onChange={handleChange} required />
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