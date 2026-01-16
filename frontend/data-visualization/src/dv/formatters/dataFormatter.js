import { rawMetadata } from '../mock_data/rawMetadata';

export function formatAlerts(rawAlerts) {
  return rawAlerts.map(alert => {
    const building = rawMetadata.buildings[alert.buildingId];
    const sev = rawMetadata.severityConfig[alert.severity];

    return {
      id: alert.id,
      buildingName: building?.name ?? alert.buildingId,
      message: alert.message,
      time: new Date(alert.timestamp).toLocaleString(),
      severity: {
        code: alert.severity,
        label: sev?.label ?? alert.severity,
        icon: sev?.icon ?? 'ℹ️',
        color: sev?.color ?? 'gray',
      },
    };
  });
}

export function formatMeasurements(rawList, meta) {
  if(!rawList || rawList.length === 0) return null;
  const firstPoint = rawList[0];
  
  let metricName = "Measurement";
  let unitName = "";
  if(firstPoint.metric === 'temperature') {
     metricName = "Temperature";
     unitName = '°C';
  }
  if(firstPoint.metric === 'power') {
    metricName = "Power Consumption";
    unitName = 'W';
  }
  if(firstPoint.metric === 'co2') {
    metricName = "CO2 Level";
    unitName = 'ppm';
  }
  if(firstPoint.metric === 'humidity') {
    metricName = "Humidity";
    unitName = '%';
  }

  const roomInfo = firstPoint.tags?.room ? ` (Room: ${firstPoint.tags.room})` : "";
  let extraInfo = "";
  if(meta && meta.devices && meta.devices[firstPoint.device_id]) {
    const deviceMeta = meta.devices[firstPoint.device_id];
    extraInfo = ` [Device: ${deviceMeta.model}]`;
  }


  return {
    seriesName: `${metricName}${roomInfo}${extraInfo}`,
    unit: unitName,
    labels: rawList.map(item => new Date(item.ts).toLocaleString([], {year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'})),
    values: rawList.map(item => item.value)
  };
}

export function formatForecasts(raw, meta) {
  if(!raw || !raw.series) return null;

  let title = "Forecast";
  let unitName = "";
  if(raw.type === 'energy_demand') {
    title = "Predicted energy demand";
    unitName = "kWh";
  }
  if(raw.type === 'temp_setpoint') {
    title = "Suggested Temperature";
    unitName = "°C";
  }
  if(raw.type === 'price') {
    title = "Costs forecast";
    unitName = "PLN/kWh";
  }

  const algoInfo = raw.algo ? ` (Model: ${raw.algo})` : "";

  let locationInfo = "";
  if(meta && meta.buildings && meta.buildings[raw.buildingId]) {
    locationInfo = ` - ${meta.buildings[raw.buildingId].name}`;
  }
  if(raw.roomId) {
    locationInfo += ` (Room: ${raw.roomId})`;
  }

  return {
    seriesName: `${title}${algoInfo}${locationInfo}`,
    unit: unitName,
    horizon: raw.horizon,
    labels: raw.series.map(item => new Date(item.ts).toLocaleString([], {year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'})),
    values: raw.series.map(item => item.value),
    confidence: raw.series.map(item => item.conf ?? null)
  };
}
