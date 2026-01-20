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
- ✅ **Full integration with real database data via DAC module**

### **Data Source:**
> ⚠️ This module retrieves **real data from the database** via the Data Access and Control (DAC) module.  
> No mock or synthetic data is used in production. MockDAC exists only for development/testing purposes.

---

## 📈 Prerequisites

Before running this module, ensure the following services are available:

| Service | Purpose | Default URL |
|---------|---------|-------------|
| **MongoDB** | Database for measurements & forecasts | `localhost:27017` |
| **DAC Module** | Data Access and Control REST API | `http://localhost:8001/api/v1` |

---

## 🚀 Setup (Windows 11)

> ⚠️ **IMPORTANT**: You MUST use a Python virtual environment. The module may NOT work correctly without it.

### **1. Create and Activate Virtual Environment**

```powershell
# Navigate to module directory
cd backend\forecast-and-optimization

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

After activation, you should see `(venv)` in your terminal prompt.

### **2. Install Dependencies**

```powershell
# With venv activated
pip install -r requirements.txt
```

### **3. Configure Environment**

```powershell
# Copy example configuration
cp .env.example .env

# Edit .env with your settings (optional - defaults work for local development)
```

**Required environment variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `FORECAST_DAC_BASE_URL` | URL of DAC REST API | `http://localhost:8001/api/v1` |
| `FORECAST_USE_MOCK_DAC` | Use mock data (dev only) | `false` |
| `FORECAST_DAC_TIMEOUT_SECONDS` | HTTP request timeout | `30.0` |

---

## ▶️ Running the Module

> ⚠️ All commands below require the virtual environment to be **activated**.

### **Production Mode (Real Data)**

Ensure DAC module is running, then:

```powershell
# Activate venv if not already active
.\venv\Scripts\activate

# Start server (connects to DAC)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🔗 Connecting to DAC at http://localhost:8001/api/v1
🚀 ForecastService initialized
```

### **Development Mode (Mock Data)**

For testing without DAC:

```powershell
$env:FORECAST_USE_MOCK_DAC="true"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
⚠️  Using MockDAC (development mode)
```

### **Access API Documentation**

Open browser: `http://localhost:8000/docs`

---

## 🧪 Testing

### **Integration Tests**

```powershell
# Terminal 1: Start server (mock mode for isolated testing)
.\venv\Scripts\activate
$env:FORECAST_USE_MOCK_DAC="true"
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Run tests
.\venv\Scripts\activate
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

### **Verify Real Data Usage**

To confirm the module uses real database data:

1. Start in **production mode** (without `FORECAST_USE_MOCK_DAC`)
2. Check server logs for: `🔗 Connecting to DAC at ...`
3. Make a forecast request
4. Check DAC module logs for incoming HTTP requests
5. Change data in MongoDB → regenerate forecast → values should change

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

### **GET /forecast/latest/{building_id}**
Get most recent forecast for a building

---

## 🏗️ Project Structure

```
forecast-and-optimization/
├── app/
│   ├── api/
│   │   └── routes.py              # FastAPI endpoints
│   ├── services/
│   │   ├── forecast_service.py    # Main orchestrator
│   │   ├── forecast_engine.py     # ML forecasting
│   │   ├── optimization_engine.py # Cost optimization
│   │   ├── ml_model_manager.py    # Model management
│   │   └── dac_client.py          # DAC HTTP client
│   ├── schemas/
│   │   ├── forecast_service.py    # Request/Response models
│   │   └── dac_interfaces.py      # DAC interface definitions
│   ├── config.py                  # Configuration settings
│   └── main.py                    # Application entry point
├── tests/
│   └── test_integration.py        # Integration tests
├── .env.example                   # Example configuration
├── requirements.txt               # Dependencies
└── README.md                      # This file
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

### **Data Flow:**

```
Database (MongoDB)
      ↓
DAC Module (REST API)
      ↓ HTTP
Forecast Module (this)
      ↓
Other Teams (AAC, Frontend)
```

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
| FR4 | Store via DAC | ✅ |
| FR5 | Historical data via DAC | ✅ |
| FR6 | Multiple horizons | ✅ |
| FR7 | Performance tracking | ✅ |
| FR8 | Authorized requests | ✅ |

---

## 🐛 Troubleshooting

### **"ModuleNotFoundError"**
Virtual environment not activated:
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### **"Port 8000 already in use"**
```powershell
uvicorn app.main:app --port 8002
```

### **"Cannot connect to DAC service"**
DAC module must be running before starting this module in production mode.

### **Tests fail - "Connection refused"**
Server must be running before running tests.

---

## 👥 Team

**Developers:** Daniyar Zhumatayev (253857) & Kuzma Martysiuk (253854)  
**University:** Lodz University of Technology  
**Course:** Software Engineering  
**Module:** Forecast and Optimization  

---

**Last Updated:** 20.01.2026
