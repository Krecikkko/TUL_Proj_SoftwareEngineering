import React, { useState } from 'react';
import './UserDashboard.css';
import { FaCog } from 'react-icons/fa'; // Używamy ikony zębatki

const UserDashboard = () => {
    const [temp, setTemp] = useState(21.5);
    const [lightOn, setLightOn] = useState(false);
    const [mode, setMode] = useState('Comfort');

    return (
        <div className="user-wrapper">
            <div className="mobile-card">
                {/* Niebieski nagłówek */}
                <header className="user-header">
                    <div className="settings-icon"><FaCog /></div>
                    <h1 style={{ margin: 0, fontSize: '1.8rem' }}>Hello, Kinga!</h1>
                    <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>Your location: Room 101</p>
                </header>

                <div className="user-content">
                    {/* Temperatura */}
                    <div className="control-box">
                        <div className="box-title">ROOM TEMPERATURE</div>
                        <div className="temp-value">{temp.toFixed(1)}*C</div>
                        <div style={{ color: '#888', fontSize: '0.9rem' }}>Target: 22*C</div>

                        <div className="controls-row">
                            <button className="btn-circle" onClick={() => setTemp(temp - 0.5)}>-</button>
                            <span style={{ fontWeight: 'bold', letterSpacing: '1px' }}>ADJUST</span>
                            <button className="btn-circle" onClick={() => setTemp(temp + 0.5)}>+</button>
                        </div>
                    </div>

                    {/* Oświetlenie */}
                    <div className="control-box">
                        <div className="switch-row">
                            <div style={{ textAlign: 'left' }}>
                                <div className="box-title" style={{ marginBottom: '5px' }}>MAIN LIGHTING</div>
                                <div style={{ fontSize: '0.8rem', color: '#888' }}>Auto-off scheduled at 6:00 PM</div>
                            </div>
                            <div
                                className={`toggle-bg ${lightOn ? 'active' : ''}`}
                                onClick={() => setLightOn(!lightOn)}
                            >
                                <div className="toggle-circle"></div>
                            </div>
                        </div>
                    </div>

                    {/* Tryb Biura */}
                    <div className="control-box">
                        <div className="box-title" style={{ textAlign: 'left' }}>OFFICE MODE</div>
                        <div className="mode-switch">
                            <button
                                className={`mode-option ${mode === 'Comfort' ? 'selected' : ''}`}
                                onClick={() => setMode('Comfort')}
                            >
                                Comfort
                            </button>
                            <button
                                className={`mode-option ${mode === 'ECO' ? 'selected' : ''}`}
                                onClick={() => setMode('ECO')}
                            >
                                ECO
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserDashboard;