from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# IMPORTS
from IMeasurement import IMeasurement, MockMeasurementRepository
from ICoreDb import ICoreDb, MockCoreDb
from IForecastRead import IForecastRead, MockForecastRepository
from DataModels4DAC import UserRole, Alert, AlertSeverity

# --- FRONTEND CONTRACTS ---
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

# --- AAC SERVICE ---
class IAccessControlAndCommunication(ABC):
    @abstractmethod
    async def login_user(self, credentials: UserLogin) -> AuthToken: pass
    @abstractmethod
    async def get_dashboard_view(self, user_token: str) -> DashboardData: pass
    @abstractmethod
    async def get_system_alerts(self, user_token: str) -> List[Alert]: pass

class AACImplementation(IAccessControlAndCommunication):
    
    def __init__(self, measurement_db, core_db, forecast_db):
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
        # Note: Accessing .metric (str) and .value
        power = sum(m.value for m in metrics if m.metric == "power_w")
        
        # 2. Fetch Forecast
        forecast = await self.fore_db.get_latest_demand_forecast("Building-1")
        # Note: Accessing .series_item list of dicts
        next_hour_val = forecast.series_item[0]["value"]
        
        # 3. Get Alerts
        alerts = await self.get_system_alerts(user_token)
        
        return DashboardData(
            current_power_usage=power,
            temperature_avg=21.5,
            active_alerts_count=len(alerts),
            forecast_summary=f"Demand expected to reach {int(next_hour_val)} kW next hour."
        )

    async def get_system_alerts(self, user_token: str) -> List[Alert]:
        generated_alerts = []
        metrics = await self.meas_db.get_building_metrics("Building-1")
        
        for m in metrics:
            # Rule 1: Temperature > 28.0
            if m.metric == "temp_c" and m.value > 28.0:
                generated_alerts.append(Alert(
                    alert_id=f"alt_{m.ts.timestamp()}",
                    severity=AlertSeverity.WARNING,
                    message=f"High Temperature: {m.value}",
                    device_id=m.deviceId # Changed from device_id
                ))
            
            # Rule 2: CO2 > 1000
            if m.metric == "co2_ppm" and m.value > 1000:
                generated_alerts.append(Alert(
                    alert_id=f"alt_{m.ts.timestamp()}",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Poor Air Quality: {m.value}",
                    device_id=m.deviceId
                ))

        return generated_alerts

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