
export const rawForecasts = [
  {
    buildingId: "B1",
    type: "energy_demand",
    horizon: "PT24H",
    lastUpdated: "2025-01-01T12:00:00Z",
    series: [
      { ts: "2025-01-01T13:00:00Z", value: 45.5, conf: 0.95 },
      { ts: "2025-01-01T14:00:00Z", value: 48.0, conf: 0.92 }
    ],
    roomId: null,  
    floorId: null,
    algo: "XGBoost v1.4"
  },

  {
    buildingId: "B1",
    roomId: "R-101",
    type: "temp_setpoint",
    horizon: "PT1H",
    lastUpdated: "2025-01-01T12:00:00Z",
    series: [
      { ts: "2025-01-01T13:00:00Z", value: 21.0 }, 
      { ts: "2025-01-01T13:15:00Z", value: 21.5 }
    ],
  }
];