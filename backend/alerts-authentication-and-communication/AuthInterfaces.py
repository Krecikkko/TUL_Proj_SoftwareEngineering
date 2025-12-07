from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# 1. IMPORTS
from .IMeasurement import IMeasurement, MockMeasurementRepository
from .ICoreDb import ICoreDb, MockCoreDb
from .IForecastRead import IForecastRead, MockForecastRepository
# Import the new Alert models
from .DataModels4DAC import MetricType, UserRole, Alert, AlertSeverity

# --- FRONTEND DATA CONTRACTS ---
class UserLogin(BaseModel):
    username: str
    password: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    role: str

class DashboardData(BaseModel):
    current_power_usage: float
    temperature_avg: float
    active_alerts_count: int
    forecast_summary: str

# --- AAC SERVICE IMPLEMENTATION ---
class IAccessControlAndCommunication(ABC):
    @abstractmethod
    async def login_user(self, credentials: UserLogin) -> AuthToken: pass
    @abstractmethod
    async def get_dashboard_view(self, user_token: str) -> DashboardData: pass
    # NEW: Add this method to the interface contract
    @abstractmethod
    async def get_system_alerts(self, user_token: str) -> List[Alert]: pass

class AACImplementation(IAccessControlAndCommunication):
    
    def __init__(self, 
                 measurement_db: IMeasurement, 
                 core_db: ICoreDb, 
                 forecast_db: IForecastRead):
        self.meas_db = measurement_db
        self.core_db = core_db
        self.fore_db = forecast_db

    async def login_user(self, credentials: UserLogin) -> AuthToken:
        user = await self.core_db.get_user_by_username(credentials.username)
        if not user or credentials.password != "secret":
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return AuthToken(
            access_token=f"token_for_{user.username}", 
            token_type="bearer", 
            role=user.role.value
        )

    async def get_dashboard_view(self, user_token: str) -> DashboardData:
        # 1. Fetch Metrics
        metrics = await self.meas_db.get_building_metrics("Building-1")
        power = sum(m.value for m in metrics if m.metric == MetricType.POWER)
        
        # 2. Fetch Forecast
        forecast = await self.fore_db.get_latest_demand_forecast("Building-1")
        next_hour_val = forecast.series[0].value
        
        # 3. Get Active Alerts Count (Calling our new logic!)
        alerts = await self.get_system_alerts(user_token)
        
        return DashboardData(
            current_power_usage=power,
            temperature_avg=21.5,
            active_alerts_count=len(alerts), # Dynamic count
            forecast_summary=f"Demand expected to reach {int(next_hour_val)} kW next hour."
        )

    async def get_system_alerts(self, user_token: str) -> List[Alert]:
        """
        Logic to DETECT malfunctions or out-of-range readings.
        """
        generated_alerts = []

        # A. Detect Out-of-Range Sensor Readings
        # We fetch the current state of the building
        metrics = await self.meas_db.get_building_metrics("Building-1")
        
        for m in metrics:
            # Rule 1: Temperature Threshold (e.g., > 28.0 C is overheating)
            if m.metric == MetricType.TEMPERATURE and m.value > 28.0:
                generated_alerts.append(Alert(
                    alert_id=f"alt_{m.reading_id}",
                    severity=AlertSeverity.WARNING,
                    message=f"High Temperature detected: {m.value}°C",
                    device_id=m.device_id,
                    timestamp=datetime.utcnow()
                ))
            
            # Rule 2: CO2 Safety Threshold (e.g., > 1000 ppm)
            if m.metric == MetricType.CO2 and m.value > 1000:
                generated_alerts.append(Alert(
                    alert_id=f"alt_{m.reading_id}",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Poor Air Quality: {m.value} ppm CO2",
                    device_id=m.device_id,
                    timestamp=datetime.utcnow()
                ))

        # B. Detect Device Malfunctions (Timeouts)
        # In a real scenario, you'd iterate a list of critical devices.
        # Here we check one specific device for demonstration.
        try:
            status = await self.meas_db.get_device_status("dev_A")
            # If last update was more than 1 hour ago -> Offline
            if datetime.utcnow() - status.updated_at > timedelta(hours=1):
                generated_alerts.append(Alert(
                    alert_id="alt_offline_A",
                    severity=AlertSeverity.CRITICAL,
                    message="Device offline for > 1 hour",
                    device_id="dev_A"
                ))
        except Exception:
            # Handle case where device isn't found
            pass

        return generated_alerts

# --- DEPENDENCY INJECTION ---
async def get_aac_service():
    return AACImplementation(
        measurement_db=MockMeasurementRepository(),
        core_db=MockCoreDb(),
        forecast_db=MockForecastRepository()
    )

router = APIRouter(prefix="/api/v1/gateway", tags=["AAC Gateway"])

@router.post("/login")
async def login(creds: UserLogin, svc: IAccessControlAndCommunication = Depends(get_aac_service)):
    return await svc.login_user(creds)

@router.get("/dashboard")
async def dashboard(token: str, svc: IAccessControlAndCommunication = Depends(get_aac_service)):
    return await svc.get_dashboard_view(token)

@router.get("/alerts")
async def alerts(token: str, svc: IAccessControlAndCommunication = Depends(get_aac_service)):
    return await svc.get_system_alerts(token)