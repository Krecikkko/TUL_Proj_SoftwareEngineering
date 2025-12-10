import React from 'react';
import './AdminDashboard.css'; // Import stylów
import EnergyChartWidget from './components/EnergyChartWidget';
import AlertsWidget from './components/AlertsWidget';

const AdminDashboard = () => {
    return (
        <div className="admin-layout">

            {/* LEWY SIDEBAR */}
            <aside className="admin-sidebar">
                <div className="sidebar-brand">ADMIN</div>
                <nav>
                    <a href="#" className="nav-item active">Dashboard</a>
                    <a href="#" className="nav-item">Energy Goals</a>
                    <a href="#" className="nav-item">Users</a>
                </nav>
            </aside>

            {/* GŁÓWNA TREŚĆ */}
            <main className="admin-content">

                {/* Nagłówek */}
                <div className="top-bar">
                    <h1 className="page-title">Building Management Panel</h1>
                    <span className="user-info">Logged In: Alicja (Administrator)</span>
                </div>

                {/* Grid z kartami (3 kafelki) */}
                <div className="cards-grid">
                    {/* Karta 1 */}
                    <div className="kpi-card">
                        <div className="kpi-label">TODAY'S CONSUMPTION</div>
                        <div className="kpi-value">450 kWh</div>
                        <div style={{ color: '#22c55e', fontSize: '0.9rem', fontWeight: 'bold', marginTop: '5px' }}>
                            ▼ 5% vs yesterday
                        </div>
                    </div>

                    {/* Karta 2 */}
                    <div className="kpi-card">
                        <div className="kpi-label">ESTIMATED COST</div>
                        <div className="kpi-value">$ 320.00</div>
                        <div style={{ color: '#6b7280', fontSize: '0.9rem', marginTop: '5px' }}>
                            Day Tariff
                        </div>
                    </div>

                    {/* Karta 3 */}
                    <div className="kpi-card">
                        <div className="kpi-label">CO2 REDUCTION GOAL</div>
                        <div className="kpi-value">85%</div>
                        <div className="progress-bar-bg">
                            <div className="progress-bar-fill" style={{ width: '85%' }}></div>
                        </div>
                    </div>
                </div>

                {/* Sekcja Wykresu */}
                <div className="chart-placeholder-box" style={{ display: 'block', height: 'auto' }}>
                    <EnergyChartWidget />
                </div>

                {/* Tabela Aktywności */}
                <div className="table-section">
                    <div className="kpi-label">RECENT SYSTEM ALERTS</div>
                    <AlertsWidget />
                </div>

            </main>
        </div>
    );
};

export default AdminDashboard;