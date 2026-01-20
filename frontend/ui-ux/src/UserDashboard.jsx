import React, { useEffect, useState } from 'react';
import './UserDashboard.css';
// Zostawiam ikonę wylogowania/ustawień jako dekorację nagłówka
import { FaCog } from 'react-icons/fa';
import { getMeasurements, getForecasts } from '../../data-visualization/src/dv/facade/dvFacade';

const UserDashboard = () => {
    // Dane z Backend
    const [currentTemp, setCurrentTemp] = useState(null);
    const [targetTemp, setTargetTemp] = useState(21.0);
    const [co2, setCo2] = useState(null);
    const [humidity, setHumidity] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            const now = new Date();
            const oneHourAgo = new Date(now.getTime() - 3600000);

            // Funkcja pomocnicza
            const fetchLast = async (metric) => {
                const res = await getMeasurements({
                    buildingId: "B1", metric: metric,
                    fromDate: oneHourAgo.toISOString(), toDate: now.toISOString()
                });
                return (res.status === 'ok' && res.data.values.length > 0)
                    ? res.data.values[res.data.values.length - 1]
                    : null;
            };

            // 1. Pobierz odczyty sensorów
            setCurrentTemp(await fetchLast("temperature"));
            setCo2(await fetchLast("co2"));
            setHumidity(await fetchLast("humidity"));

            // 2. Pobierz cel (Forecast type: temp_setpoint)
            const fore = await getForecasts({
                buildingId: "B1", type: "temp_setpoint",
                fromDate: oneHourAgo.toISOString(), toDate: now.toISOString()
            });
            if (fore.status === 'ok' && fore.data.values.length > 0) {
                setTargetTemp(fore.data.values[0]);
            }
        };
        fetchData();
    }, []);

    // Lokalna zmiana celu (w prawdziwej aplikacji wysłałaby POST do backendu)
    const handleTempChange = (delta) => setTargetTemp(prev => parseFloat((prev + delta).toFixed(1)));

    return (
        <div className="user-wrapper">
            <div className="mobile-card">
                <header className="user-header">
                    <div className="settings-icon"><FaCog /></div>
                    <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Hello</h1>
                    <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>Building User Panel</p>
                </header>

                <div className="user-content">
                    {/* TERMOSTAT */}
                    <div className="control-box">
                        <div className="box-title">CURRENT TEMPERATURE</div>
                        <div className="temp-value">
                            {currentTemp ? currentTemp.toFixed(1) : '--'}°C
                        </div>
                        <div className="controls-row">
                            <button className="btn-circle" onClick={() => handleTempChange(-0.5)}>-</button>
                            <div style={{textAlign: 'center'}}>
                                <span style={{display: 'block', fontSize: '0.7rem', color: '#888'}}>TARGET</span>
                                <span style={{fontWeight: 'bold', fontSize: '1.2rem'}}>{targetTemp} °C</span>
                            </div>
                            <button className="btn-circle" onClick={() => handleTempChange(0.5)}>+</button>
                        </div>
                    </div>

                    {/* JAKOŚĆ POWIETRZA */}
                    <div style={{display: 'flex', gap: '15px'}}>
                        <div className="control-box" style={{flex: 1, padding: '15px'}}>
                            <div className="box-title" style={{marginBottom: '5px'}}>CO2</div>
                            <div style={{fontSize: '1.2rem', fontWeight: 'bold', color: co2 > 1000 ? '#dc2626' : '#10b981'}}>
                                {co2 ? Math.round(co2) : '--'} <small style={{fontSize: '0.7rem', color: '#888'}}>ppm</small>
                            </div>
                        </div>
                        <div className="control-box" style={{flex: 1, padding: '15px'}}>
                            <div className="box-title" style={{marginBottom: '5px'}}>HUMIDITY</div>
                            <div style={{fontSize: '1.2rem', fontWeight: 'bold', color: '#2563eb'}}>
                                {humidity ? Math.round(humidity) : '--'} <small style={{fontSize: '0.7rem', color: '#888'}}>%</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserDashboard;