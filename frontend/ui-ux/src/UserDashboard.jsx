import React, { useEffect, useState } from 'react';
import './UserDashboard.css';
import { FaCog } from 'react-icons/fa';
import { getMeasurements, getForecasts } from '../../data-visualization/src/dv/facade/dvFacade';

const UserDashboard = () => {
    const [currentTemp, setCurrentTemp] = useState(null);
    const [targetTemp, setTargetTemp] = useState(22.0); // Dajemy domyślną wartość startową
    const [lightOn, setLightOn] = useState(false);
    const [mode, setMode] = useState('Comfort');

    useEffect(() => {
        const fetchData = async () => {
            // 1. Pobierz obecną temperaturę
            const meas = await getMeasurements({
                buildingId: "B1", metric: "temperature", deviceId: "dev_temp_001",
                fromDate: "2025-01-01", toDate: "2025-01-02"
            });
            if (meas.status === 'ok') setCurrentTemp(meas.data.values[0]);

            // 2. Pobierz cel (Target) z bazy
            const fore = await getForecasts({
                buildingId: "B1", type: "temp_setpoint",
                fromDate: "2025-01-01", toDate: "2025-01-02"
            });
            // Jeśli baza coś zwróciła, nadpisujemy nasz cel
            if (fore.status === 'ok' && fore.data.values.length > 0) {
                setTargetTemp(fore.data.values[0]);
            }
        };
        fetchData();
    }, []);

    // --- LOGIKA PRZYCISKÓW ---
    const handleDecrease = () => {
        setTargetTemp(prev => (prev ? prev - 0.5 : 20.0));
    };

    const handleIncrease = () => {
        setTargetTemp(prev => (prev ? prev + 0.5 : 24.0));
    };

    return (
        <div className="user-wrapper">
            <div className="mobile-card">
                <header className="user-header">
                    <div className="settings-icon"><FaCog /></div>
                    <h1 style={{ margin: 0, fontSize: '1.8rem' }}>Hello, Kinga!</h1>
                    <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>Your location: Room 101</p>
                </header>

                <div className="user-content">
                    <div className="control-box">
                        <div className="box-title">ROOM TEMPERATURE</div>
                        <div className="temp-value">
                            {currentTemp ? currentTemp.toFixed(1) : '--'}°C
                        </div>
                        <div style={{ color: '#888', fontSize: '0.9rem' }}>
                            {/* Wyświetlamy Target, który możemy zmieniać */}
                            Target: {targetTemp ? targetTemp.toFixed(1) : '--'}°C
                        </div>

                        <div className="controls-row">
                            {/* Podpinamy funkcje pod przyciski */}
                            <button className="btn-circle" onClick={handleDecrease}>-</button>
                            <span style={{ fontWeight: 'bold' }}>ADJUST</span>
                            <button className="btn-circle" onClick={handleIncrease}>+</button>
                        </div>
                    </div>

                    <div className="control-box">
                        <div className="switch-row">
                            <div style={{ textAlign: 'left' }}>
                                <div className="box-title">MAIN LIGHTING</div>
                                <div style={{ fontSize: '0.8rem', color: '#888' }}>Auto-off scheduled at 6:00 PM</div>
                            </div>
                            <div className={`toggle-bg ${lightOn ? 'active' : ''}`} onClick={() => setLightOn(!lightOn)}>
                                <div className="toggle-circle"></div>
                            </div>
                        </div>
                    </div>

                    <div className="control-box">
                        <div className="box-title" style={{ textAlign: 'left' }}>OFFICE MODE</div>
                        <div className="mode-switch">
                            <button className={`mode-option ${mode === 'Comfort' ? 'selected' : ''}`} onClick={() => setMode('Comfort')}>Comfort</button>
                            <button className={`mode-option ${mode === 'ECO' ? 'selected' : ''}`} onClick={() => setMode('ECO')}>ECO</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserDashboard;