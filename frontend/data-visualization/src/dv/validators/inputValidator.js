import { rawMetadata } from "../mock_data/rawMetadata";

export function validate(params) {
  const errors = [];

  const { fromDate, toDate, buildingId } = params;

  if (!fromDate) errors.push('Lack of date "from".');
  if (!toDate) errors.push('Lack of date "until".');

  if (fromDate && toDate) {
    if (new Date(fromDate) > new Date(toDate)) {
      errors.push('"From" cannot exceed "until".');
    }
  }

  if (!buildingId) {
    errors.push("No Building ID provided.");
  } else {
    if (!rawMetadata.buildings[buildingId]) {
      errors.push(`Building "${buildingId}" does not exist.`);
    }
  }

  return {
    ok: errors.length === 0,
    errors,
  };
}

export function normalize(params) {
  return {
    buildingId: params.buildingId,
    timeRange: {
      from: new Date(params.fromDate).toISOString(),
      to: new Date(params.toDate).toISOString(),
    },
  };
}