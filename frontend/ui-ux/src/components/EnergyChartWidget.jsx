import React, { useEffect, useState } from 'react';
import { getMeasurements } from '../../../data-visualization/src/dv/facade/dvFacade';

const EnergyChartWidget = () => {
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);
    const today = new Date();

    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);

    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);

    const fromDate = yesterday.toISOString().slice(0, 10);
    const toDate = tomorrow.toISOString().slice(0, 10);
    useEffect(() => {
        const loadData = async () => {
            // Pytamy o MOC (Power)
            const query = {
                buildingId: "B1",
                metric: "power",
                fromDate: fromDate,
                toDate: toDate
            };

            try {
                const result = await getMeasurements(query);
                console.log("Fetched Measurements for EnergyChartWidget:", result);
                if (result.status === 'ok') {
                    setChartData(result.data);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    if (loading) return <div style={{padding: '20px'}}>Loading...</div>;
    if (!chartData) return <div style={{padding: '20px', color: 'red'}}>No data signal.</div>;

    // Maksymalna wartość do skalowania wykresu (np. 6000 Watt)
    const MAX_VALUE = 6000;

    return (
        <div style={{ width: '100%', padding: '10px' }}>
            <div style={{ marginBottom: '15px' }}>
                {/* Wyświetlamy nazwę z bazy (Licznik Główny) */}
                <h4 style={{ margin: 0, color: '#64748b', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                    {chartData.seriesName}
                </h4>
                <small style={{ color: '#94a3b8' }}>Unit: {chartData.unit}</small>
            </div>

            <div style={{
                display: 'flex',
                alignItems: 'flex-end',
                gap: '10px', // Większy odstęp między słupkami
                height: '180px',
                borderBottom: '1px solid #e2e8f0',
                paddingBottom: '5px'
            }}>
                {chartData.values.map((val, i) => (
                    <div key={i} style={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        minWidth: '20px'
                    }}>
                        {/* SŁUPEK */}
                        <div
                            style={{
                                // Używamy pikseli dla pewności. Jeśli wartość to 4500, słupek będzie wysoki.
                                height: `${Math.min((val / MAX_VALUE) * 150, 150)}px`,
                                width: '100%',
                                backgroundColor: '#2563eb', // Wyraźny niebieski
                                borderRadius: '4px 4px 0 0',
                                minHeight: '4px' // Żeby zawsze było widać choć kawałek
                            }}
                            title={`Moc: ${val} W`} // Po najechaniu myszką pokaże wartość
                        ></div>

                        {/* GODZINA */}
                        <span style={{ fontSize: '10px', color: '#94a3b8', marginTop: '6px', transform: 'rotate(-45deg)', whiteSpace: 'nowrap'}}>
                           {chartData.labels[i].split(',')[1] || chartData.labels[i]}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EnergyChartWidget;