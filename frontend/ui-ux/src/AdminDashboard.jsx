import React, { useEffect, useState } from 'react';
import './AdminDashboard.css';
import EnergyChartWidget from './components/EnergyChartWidget';
import AlertsWidget from './components/AlertsWidget';
// Upewnij się, że ścieżka do fasady jest poprawna w Twoim projekcie!
import { getDashboardStats } from '../../data-visualization/src/dv/facade/dvFacade';

const AdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            // Pobieramy dane KPI dla budynku B1
            const data = await getDashboardStats("B1");
            if (data) setStats(data);
            setLoading(false);
        };
        fetchData();
    }, []);

    // Pobieramy rolę z localStorage, jeśli brak - wyświetlamy ogólną nazwę
    const role = localStorage.getItem('userRole') || 'Administrator';

    return (
        <div className="admin-layout">
            <aside className="admin-sidebar">
                <div className="sidebar-brand">ADMIN</div>
                <nav>
                    {/* Tylko Overview, bo tylko to mamy w danych */}
                    <a href="#" className="nav-item active">Overview</a>
                </nav>
            </aside>

            <main className="admin-content">
                <div className="top-bar">
                    <h1 className="page-title">Building Management Panel</h1>
                    <span className="user-info">
                        Logged In: <strong style={{textTransform: 'capitalize'}}>{role}</strong>
                    </span>
                </div>

                {/* KPI CARDS */}
                <div className="cards-grid">
                    <div className="kpi-card">
                        <div className="kpi-label">CURRENT POWER</div>
                        <div className="kpi-value" style={{ color: '#2563eb' }}>
                            {loading ? "..." : stats?.current_power_usage ?? "--"} <span style={{fontSize: '1rem'}}>W</span>
                        </div>
                        <div style={{ color: '#22c55e', fontSize: '0.9rem', fontWeight: 'bold', marginTop: '5px' }}>
                            Live Measurement
                        </div>
                    </div>

                    <div className="kpi-card">
                        <div className="kpi-label">AVG TEMP</div>
                        <div className="kpi-value" style={{ color: '#f59e0b' }}>
                            {loading ? "..." : stats?.temperature_avg ?? "--"} <span style={{fontSize: '1rem'}}>°C</span>
                        </div>
                        <div style={{ color: '#6b7280', fontSize: '0.9rem', marginTop: '5px' }}>
                            Building Average
                        </div>
                    </div>

                    <div className="kpi-card">
                        <div className="kpi-label">ACTIVE ALERTS</div>
                        <div className="kpi-value" style={{ color: '#dc2626' }}>
                            {loading ? "..." : stats?.active_alerts_count ?? "0"}
                        </div>
                        <div className="progress-bar-bg">
                            <div
                                className="progress-bar-fill"
                                style={{
                                    width: stats?.active_alerts_count > 0 ? '40%' : '100%',
                                    background: stats?.active_alerts_count > 0 ? '#dc2626' : '#22c55e'
                                }}
                            ></div>
                        </div>
                    </div>
                </div>

                {/* AI SUMMARY */}
                {stats?.forecast_summary && (
                    <div style={{ background: '#e0f2fe', padding: '15px', borderRadius: '12px', marginBottom: '20px', color: '#0369a1', borderLeft: '5px solid #0ea5e9' }}>
                        <strong>AI Forecast:</strong> {stats.forecast_summary}
                    </div>
                )}

                {/* CHART WIDGET */}
                <div className="chart-placeholder-box" style={{ display: 'block', height: 'auto', marginBottom: '20px' }}>
                    <h3 style={{marginTop: 0, color: '#475569', fontSize: '1rem', textTransform: 'uppercase'}}>Energy Consumption</h3>
                    <EnergyChartWidget />
                </div>

                {/* ALERTS WIDGET */}
                <div className="table-section">
                    <div className="kpi-label">RECENT SYSTEM ALERTS</div>
                    <AlertsWidget />
                </div>
            </main>
        </div>
    );
};

export default AdminDashboard;