import { validate, normalize } from '../validators/inputValidator';
import { formatAlerts, formatForecasts, formatMeasurements } from '../formatters/dataFormatter';
import { rawAlerts } from '../mock_data/rawAlerts';
import { rawMeasurements } from '../mock_data/rawMeasurements';
import { rawForecasts } from '../mock_data/rawForecasts';
import { rawMetadata } from '../mock_data/rawMetadata';

async function fetchAlertsFromAAC(query) {
  console.log("Simulation of query to AAC:", query);
  const filtered = rawAlerts.filter(a => a.buildingId === query.buildingId);
  return filtered;
}

export async function getAlerts(inputParams) {
  const validation = validate(inputParams);
  if (!validation.ok) {
    return { status: 'validation-error', errors: validation.errors };
  }

  const query = normalize(inputParams);
  const raw = await fetchAlertsFromAAC(query);
  const formatted = formatAlerts(raw);

  return {
    status: 'ok',
    data: formatted,
  };
}

async function fetchMeasurements(query) {
  console.log("Simulation of query to AAC:", query);

  const targetMetric = query.metric || 'temperature';
  const filtered = rawMeasurements.filter(item => {
    const buildingMatch = item.buildingId === query.buildingId;
    const metricMatch = item.metric === targetMetric;
    const deviceMatch = query.deviceId ? item.device_id === query.deviceId : true;
    return buildingMatch && metricMatch && deviceMatch;
  });
  return filtered;
}

export async function getMeasurements(inputParams) {
  const validation = validate(inputParams);
  if(!validation.ok) {
    return {status: 'validation-error', errors: validation.errors};
  }

  const normalizedParams =normalize(inputParams);

  const query = {
    ...normalizedParams,
    metric: inputParams.metric,
    deviceId: inputParams.deviceId
  };
  const rawData = await fetchMeasurements(query);
  if(!rawData || rawData.length === 0) {
    return { status: 'no-data', message: "No measurements found"};
  }
  const meta = rawMetadata;
  const formatted = formatMeasurements(rawData, meta);

  return {status: 'ok', data: formatted};
}

async function fetchForecasts(query) {
  console.log("Simulation of query to AAC:", query);

  const targetType = query.type || 'energy_demand';

  const foundForecast = rawForecasts.find(item =>
    item.buildingId === query.buildingId &&
    item.type === targetType
  );
  return foundForecast;
}

export async function getForecasts(inputParams) {
  const validation = validate(inputParams);
  if(!validation.ok) {
    return {status: 'validation-error', errors: validation.errors};
  }

  const normalizedParams = normalize(inputParams);
  const query = {
    ...normalizedParams,
    type: inputParams.type
  };
  const rawData = await fetchForecasts(query);

  if(!rawData) {
    return { status: 'no-data', message: "No forecasts found"};
  }
  const meta = rawMetadata;
  const formatted = formatForecasts(rawData, meta);

  return {status: 'ok', data: formatted};
}
