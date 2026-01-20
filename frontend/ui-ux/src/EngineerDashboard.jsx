import React, { useState, useEffect } from 'react';
import './EngineerDashboard.css';
import { FaSearch, FaWrench, FaExclamationCircle } from 'react-icons/fa';
import { getMeasurements, getAlerts } from '../../data-visualization/src/dv/facade/dvFacade';

const EngineerDashboard = () => {
    // Stan wyszukiwania - domyślnie pusty
    const [searchQuery, setSearchQuery] = useState('');
    const [activeDeviceId, setActiveDeviceId] = useState(null);

    // Dane z DV
    const [chartData, setChartData] = useState(null);
    const [criticalAlerts, setCriticalAlerts] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!activeDeviceId) return; // Nie pobieraj, dopóki inżynier nie wpisze ID

        const fetchDiagnostics = async () => {
            setLoading(true);
            const now = new Date();
            const start = new Date(now.getTime() - 24 * 60 * 60 * 1000); // 24h wstecz

            // 1. Telemetria
            const meas = await getMeasurements({
                buildingId: "B1",
                metric: "temperature",
                deviceId: activeDeviceId,
                fromDate: start.toISOString(),
                toDate: now.toISOString()
            });
            setChartData(meas.status === 'ok' ? meas.data : null);

            // 2. Alerty (tylko HIGH)
            const alertsRes = await getAlerts({
                buildingId: "B1",
                fromDate: start.toISOString(),
                toDate: now.toISOString()
            });
            if (alertsRes.status === 'ok') {
                const high = alertsRes.data.filter(a => a.severity.label === 'HIGH');
                setCriticalAlerts(high);
            }
            setLoading(false);
        };

        fetchDiagnostics();
    }, [activeDeviceId]);

    const handleSearch = (e) => {
        e.preventDefault();
        if(searchQuery.trim()) setActiveDeviceId(searchQuery);
    };

    const role = localStorage.getItem('userRole') || 'Maintenance Engineer';

    return (
        <div className="engineer-layout">
            <aside className="engineer-sidebar">
                <div className="sidebar-brand" style={{color: '#f59e0b'}}>MAINTENANCE</div>
                <nav>
                    {/* Tylko to, co daje backend */}
                    <a href="#" className="nav-item active">System Diagnostics</a>
                </nav>
            </aside>

            <main className="engineer-content">
                <div className="top-bar">
                    <h1 className="page-title">Engineer Diagnostics</h1>
                    <span className="user-info">
                        Logged In: <strong style={{textTransform: 'capitalize'}}>{role}</strong>
                    </span>
                </div>

                {/* Wyszukiwarka */}
                <div className="search-section">
                    <form onSubmit={handleSearch} className="device-search-form">
                        <FaSearch className="search-icon"/>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Enter Device ID (e.g., dev_temp_001)..."
                            className="search-input"
                        />
                        <button type="submit" className="search-btn">DIAGNOSE</button>
                    </form>
                </div>

                <div className="engineer-grid">
                    {/* Wykres */}
                    <div className="diag-card chart-area">
                        <div className="card-header">
                            <FaWrench /> DEVICE TELEMETRY: {activeDeviceId || '---'}
                        </div>
                        <div className="chart-container">
                            {!activeDeviceId && <p style={{color: '#888', padding: '20px'}}>Enter Device ID to start diagnostics.</p>}
                            {loading && <p style={{padding: '20px'}}>Loading data...</p>}
                            {!loading && activeDeviceId && !chartData && <p style={{color: '#888', padding: '20px'}}>No signal found for this ID.</p>}

                            {!loading && chartData && (
                                <div style={{display: 'flex', alignItems: 'flex-end', height: '200px', gap: '5px', padding: '10px'}}>
                                    {chartData.values.map((val, i) => (
                                        <div key={i} style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
                                            <div style={{
                                                width: '100%',
                                                height: `${Math.min(val * 5, 180)}px`,
                                                background: '#f59e0b',
                                                borderRadius: '2px'
                                            }} title={val}></div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Alerty */}
                    <div className="diag-card alerts-area">
                        <div className="card-header" style={{color: '#dc2626'}}>
                            <FaExclamationCircle /> CRITICAL ALERTS (HIGH)
                        </div>
                        <div className="alerts-list">
                            {criticalAlerts.length === 0 ? (
                                <p style={{padding: '20px', color: '#10b981'}}>No critical issues found.</p>
                            ) : (
                                criticalAlerts.map(alert => (
                                    <div key={alert.id} className="critical-alert-item">
                                        <div className="alert-time">{alert.time}</div>
                                        <div className="alert-msg">{alert.message}</div>
                                        <div className="alert-badge">HIGH</div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default EngineerDashboard;