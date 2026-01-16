from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# IMPORTS
from IMeasurement import IMeasurement, MockMeasurementRepository
from ICoreDb import ICoreDb, MockCoreDb
from IForecastRead import IForecastRead, MockForecastRepository
from DataModels4DAC import (
    UserRole, Alert, AlertSeverity, Measurement, 
    MeasurementResponse, ForecastResponse, Forecast
)

# --- FRONTEND CONTRACTS (Auth) ---
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

# --- AAC SERVICE INTERFACE ---
class IAccessControlAndCommunication(ABC):
    @abstractmethod
    async def login_user(self, credentials: UserLogin) -> AuthToken: pass
    @abstractmethod
    async def get_dashboard_view(self, user_token: str) -> DashboardData: pass
    @abstractmethod
    async def get_system_alerts(self, user_token: str) -> List[Alert]: pass
    
    # NEW METHODS FOR DATA VIZ
    @abstractmethod
    async def get_measurements_view(
        self, buildingId: str, metric: str, fromDate: datetime, toDate: datetime, deviceId: Optional[str] = None
    ) -> List[MeasurementResponse]: pass

    @abstractmethod
    async def get_forecasts_view(
        self, buildingId: str, type: str, fromDate: datetime, toDate: datetime
    ) -> Optional[ForecastResponse]: pass

# --- AAC IMPLEMENTATION ---
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
        # Dashboard Logic (unchanged but uses new mapping internally if needed)
        target_building = "B1" # Updated to match Frontend Mock ID
        end = datetime.utcnow()
        start = end - timedelta(hours=24)
        
        power_metrics = await self.meas_db.get_measurements(target_building, "power_w", start, end)
        current_power = sum(m.value for m in power_metrics)
        
        temp_metrics = await self.meas_db.get_measurements(target_building, "temp_c", start, end)
        avg_temp = sum(m.value for m in temp_metrics) / len(temp_metrics) if temp_metrics else 0.0

        forecast = await self.fore_db.get_latest_forecast(target_building, "energy_demand", "1D")
        summary = "No data"
        if forecast and forecast.series_item:
            val = int(forecast.series_item[0]["value"])
            summary = f"Demand expected to reach {val} kW."
            
        alerts = await self.get_system_alerts(user_token)
        
        return DashboardData(
            current_power_usage=round(current_power, 2),
            temperature_avg=round(avg_temp, 1),
            active_alerts_count=len(alerts),
            forecast_summary=summary
        )

    async def get_system_alerts(self, user_token: str) -> List[Alert]:
        generated_alerts = []
        target_building = "B1" # Match Frontend ID
        end = datetime.utcnow()
        start = end - timedelta(minutes=60)

        # 1. Check Temperature (Frontend: HIGH/MEDIUM/LOW)
        temps = await self.meas_db.get_measurements(target_building, "temp_c", start, end)
        for m in temps:
            if m.value > 28.0:
                generated_alerts.append(Alert(
                    id=f"alert_{m.id}",
                    building_id=target_building,
                    severity=AlertSeverity.MEDIUM, # Orange
                    message=f"High Temperature: {m.value}°C",
                    device_id=m.device_id
                ))

        # 2. Check CO2
        co2s = await self.meas_db.get_measurements(target_building, "co2_ppm", start, end)
        for m in co2s:
            if m.value > 1000:
                generated_alerts.append(Alert(
                    id=f"alert_{m.id}",
                    building_id=target_building,
                    severity=AlertSeverity.HIGH, # Red
                    message=f"Poor Air Quality: {m.value} ppm",
                    device_id=m.device_id
                ))
        return generated_alerts

    # --- NEW: DATA VIZ TRANSLATION METHODS ---

    async def get_measurements_view(
        self, buildingId: str, metric: str, fromDate: datetime, toDate: datetime, deviceId: Optional[str] = None
    ) -> List[MeasurementResponse]:
        
        # MAP FRONTEND NAMES -> DAC CODES
        metric_map = {
            "temperature": "temp_c",
            "power": "power_w",
            "humidity": "humidity_pct",
            "co2": "co2_ppm"
        }
        dac_metric = metric_map.get(metric, metric) # Default to input if no map found

        # CALL DAC
        raw_data = await self.meas_db.get_measurements(
            building_id=buildingId,
            metric_type=dac_metric,
            start_date=fromDate,
            end_date=toDate,
            device_ids=[deviceId] if deviceId else None
        )

        # TRANSLATE BACK TO FRONTEND FORMAT
        response_list = []
        for r in raw_data:
            response_list.append(MeasurementResponse(
                ts=r.timestamp,  # Map timestamp -> ts
                value=r.value,
                metric=metric,   # Return the name frontend asked for
                device_id=r.device_id,
                buildingId=buildingId
            ))
        return response_list

    async def get_forecasts_view(
        self, buildingId: str, type: str, fromDate: datetime, toDate: datetime
    ) -> Optional[ForecastResponse]:
        
        # DAC "horizon" is hardcoded to "1D" for this example, 
        # but normally we might pick based on date range.
        raw_forecast = await self.fore_db.get_latest_forecast(
            building_id=buildingId,
            forecast_type=type,
            horizon="1D"
        )

        if not raw_forecast:
            return None

        # MAP DAC STRUCTURE -> FRONTEND STRUCTURE
        # Frontend needs 'series', DAC has 'series_item'
        return ForecastResponse(
            buildingId=buildingId,
            type=raw_forecast.type,
            horizon=raw_forecast.horizon,
            series=raw_forecast.series_item, # Map series_item -> series
            algo=raw_forecast.model_meta.get("algo")
        )

# --- ROUTER CONFIGURATION ---
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

# NEW ENDPOINTS FOR DATA VIZ
@router.get("/measurements")
async def get_measurements(
    buildingId: str, 
    metric: str, 
    fromDate: datetime, 
    toDate: datetime, 
    deviceId: Optional[str] = None,
    svc: IAccessControlAndCommunication = Depends(get_aac_service)
):
    return await svc.get_measurements_view(buildingId, metric, fromDate, toDate, deviceId)

@router.get("/forecasts")
async def get_forecasts(
    buildingId: str, 
    type: str, 
    fromDate: datetime, 
    toDate: datetime,
    svc: IAccessControlAndCommunication = Depends(get_aac_service)
):
    return await svc.get_forecasts_view(buildingId, type, fromDate, toDate)