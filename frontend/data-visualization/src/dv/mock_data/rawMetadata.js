export const rawMetadata = {
  buildings: {
    B1: { name: 'Office 1' },
    B2: { name: 'Warehouse 2' },
    B3: { name: 'Office 3'},
  },
  severityConfig: {
    HIGH:   { color: 'red', icon: '!!!', label: 'High' },
    MEDIUM: { color: 'orange', icon: '!!', label: 'Medium' },
    LOW:    { color: 'green', icon: '!', label: 'Low' },
  },
  devices: {
    'dev_temp_001': { model: 'Xiaomi Aqara', type: 'Czujnik Temperatury' },
    'dev_power_main': { model: 'Licznik Główny', type: 'Licznik Energii' },
    'dev_hvac_01': { model: 'Klimatyzator Samsung', type: 'HVAC' }
  },
  
  zones: {
    'z1': { name: 'Open Space' },
    'z2': { name: 'Serwerownia' }
  }
};
