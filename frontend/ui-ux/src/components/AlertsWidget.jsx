import React, { useEffect, useState } from 'react';
import { getAlerts } from '../../../data-visualization/src/dv/facade/dvFacade';

const AlertsWidget = () => {
    const [alerts, setAlerts] = useState([]);

    useEffect(() => {
        const fetchAlerts = async () => {
            // Musimy podać daty, inaczej ich moduł zwraca błąd walidacji!
            const result = await getAlerts({
                buildingId: 'B1',
                fromDate: "2025-01-01", // Zakres danych testowych
                toDate: "2025-01-05"
            });

            if (result.status === 'ok') {
                setAlerts(result.data);
            }
        };
        fetchAlerts();
    }, []);

    if (alerts.length === 0) return <div style={{padding: 20, color: '#64748b'}}>No active alerts found in database.</div>;

    return (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '15px' }}>
            <thead>
            <tr style={{ borderBottom: '2px solid #e5e7eb', textAlign: 'left' }}>
                <th style={{ padding: '10px', color: '#6b7280', fontSize: '0.8rem' }}>SEVERITY</th>
                <th style={{ padding: '10px', color: '#6b7280', fontSize: '0.8rem' }}>MESSAGE</th>
                <th style={{ padding: '10px', color: '#6b7280', fontSize: '0.8rem' }}>TIME</th>
            </tr>
            </thead>
            <tbody>
            {alerts.map((alert) => (
                <tr key={alert.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '12px' }}>
                            <span style={{
                                color: alert.severity.color,
                                fontWeight: 'bold',
                                fontSize: '0.8rem',
                                border: `1px solid ${alert.severity.color}`,
                                padding: '2px 6px',
                                borderRadius: '4px'
                            }}>
                                {alert.severity.icon} {alert.severity.label}
                            </span>
                    </td>
                    <td style={{ padding: '12px', color: '#374151', fontSize: '0.9rem' }}>{alert.message}</td>
                    <td style={{ padding: '12px', color: '#9ca3af', fontSize: '0.85rem' }}>{alert.time}</td>
                </tr>
            ))}
            </tbody>
        </table>
    );
};

export default AlertsWidget;