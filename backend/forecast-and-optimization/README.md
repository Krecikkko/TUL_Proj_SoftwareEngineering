# Forecast and Optimization Module

**Team**: Daniyar Zhumatayev & Kuzma Martysiuk  
**Module**: Backend - Forecast and Optimization  
**Course**: Software Engineering, Lodz University of Technology

---

## 📋 Overview

ML-powered energy forecasting and cost optimization for intelligent buildings.

### **Features:**
- ✅ Energy consumption forecasting (LSTM & XGBoost)
- ✅ Cost optimization recommendations (Polish złoty - PLN)
- ✅ Multiple forecast horizons (24H, 7D)
- ✅ Model performance tracking
- ✅ Integration with DAC module

---

## 🚀 Quick Start (Windows 11)

### **1. Setup Virtual Environment**

```powershell
# Navigate to module directory
cd backend\forecast-and-optimization

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Run the Server**

```powershell
# Make sure venv is activated (you should see (venv) in prompt)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Access API Documentation**

Open browser: `http://localhost:8000/docs`

---

## 🧪 Running Tests

### **Integration Tests** (Recommended)

```powershell
# Terminal 1: Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Run tests
python tests\test_integration.py
```

**Expected output:**
```
✅ PASSED: Health Check
✅ PASSED: Generate Forecast
✅ PASSED: Generate Optimization
✅ PASSED: Root Endpoint

RESULTS: 4/4 tests passed
```

---

## 📚 API Endpoints

### **POST /forecast**
Generate energy forecast
```json
{
  "building_id": "B001",
  "horizon": "24H",
  "forecast_type": "energy_demand",
  "requested_by": "user_id"
}
```

### **POST /optimization**
Get cost-saving recommendations
```json
{
  "building_id": "B001",
  "requested_by": "user_id",
  "time_range_hours": 24
}
```

### **GET /health**
Health check

---

## 🏗️ Project Structure

```
forecast-and-optimization/
├── app/
│   ├── api/
│   │   └── routes.py          # FastAPI endpoints
│   ├── services/
│   │   ├── forecast_service.py    # Main orchestrator
│   │   ├── forecast_engine.py     # ML forecasting
│   │   ├── optimization_engine.py # Cost optimization
│   │   └── ml_model_manager.py    # Model management
│   ├── schemas/
│   │   ├── forecast_service.py    # Request/Response models
│   │   └── dac_interfaces.py      # DAC interface definitions
│   └── main.py                # Application entry point
├── tests/
│   └── test_integration.py    # Integration tests
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

---

## 🔌 Integration with Other Teams

### **For AAC Team:**

Call our endpoints via HTTP:
```python
import requests

response = requests.post(
    "http://localhost:8000/forecast",
    json={
        "building_id": "B001",
        "horizon": "24H",
        "forecast_type": "energy_demand",
        "requested_by": "user_id"
    }
)
forecast = response.json()
```

### **For DAC Team:**

We need these interfaces (defined in `app/schemas/dac_interfaces.py`):
- `IMeasurement.get_measurements()` - Historical sensor data
- `IForecastWrite.create_forecast()` - Store forecasts
- `ICoreDb.get_building()` - Building metadata

Replace `MockDAC` in `app/main.py` with your implementation.

---

## 🇵🇱 Polish Localization

- **Currency:** PLN (złoty)
- **Energy Pricing** (2025 tariffs):
  - Peak (9-21): 1.05 zł/kWh
  - Off-peak: 0.65 zł/kWh
  - Super off-peak (23-6): 0.45 zł/kWh

---

## 📊 Functional Requirements

| FR | Requirement | Status |
|----|-------------|--------|
| FR1 | Energy forecasts | ✅ |
| FR2 | Cost forecasts | ✅ |
| FR3 | Optimization recommendations | ✅ |
| FR4 | Store via DAC | ✅ Interface defined |
| FR5 | Historical data | ✅ Via DAC |
| FR6 | Multiple horizons | ✅ |
| FR7 | Performance tracking | ✅ |
| FR8 | Authorized requests | ✅ |

---

## 🐛 Troubleshooting

### **"ModuleNotFoundError"**
Make sure venv is activated:
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### **"Port 8000 already in use"**
```powershell
# Use different port
uvicorn app.main:app --port 8001
```

### **Tests fail - "Connection refused"**
Server must be running before running tests.

---

## 👥 Team

**Developers:** Daniyar Zhumatayev (253857) & Kuzma Martysiuk (253854)
**University:** Lodz University of Technology  
**Course:** Software Engineering
**Module:** Forecast and Optimization  

---

**Last Updated:** 07.12.2025
