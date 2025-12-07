# FILE: backend/components/aac/service.py (Formerly AuthInterfaces.py)
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod

# 1. IMPORTS
# Import the definition AND the mock from the other file
from ..dac.interfaces.IMeasurement import IMeasurement, MockMeasurementRepository
from ..dac.models.DataModels4DAC import MetricType

# --- DATA MODELS (Contract with Frontend) ---
class UserLogin(BaseModel):
    username: str
    password: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    role: str

class Alert(BaseModel):
    alert_id: str
    severity: str
    message: str
    timestamp: str

class DashboardData(BaseModel):
    current_power_usage: float
    temperature_avg: float
    active_alerts_count: int
    forecast_summary: str

# --- THE AAC INTERFACE ---
class IAccessControlAndCommunication(ABC):
    @abstractmethod
    async def login_user(self, credentials: UserLogin) -> AuthToken: pass

    @abstractmethod
    async def get_dashboard_view(self, user_token: str) -> DashboardData: pass

    @abstractmethod
    async def get_system_alerts(self, user_token: str) -> List[Alert]: pass

# --- IMPLEMENTATION (The Gateway) ---
class AACImplementation(IAccessControlAndCommunication):
    
    def __init__(self, measurement_provider: IMeasurement):
        # Dependency Injection! We ask for the interface, not the specific class.
        self.measurement_provider = measurement_provider

    async def login_user(self, credentials: UserLogin) -> AuthToken:
        return AuthToken(access_token="mock_token_123", token_type="bearer", role="admin")

    async def get_dashboard_view(self, user_token: str) -> DashboardData:
        # REAL LOGIC:
        # 1. Call the Data Access mock to get real metrics
        building_metrics = await self.measurement_provider.get_building_metrics("Building-1")
        
        # 2. Process the data (Aggregation)
        power_usage = sum(m.value for m in building_metrics if m.metric == MetricType.POWER)
        temps = [m.value for m in building_metrics if m.metric == MetricType.TEMPERATURE]
        avg_temp = sum(temps) / len(temps) if temps else 0.0

        # [cite_start]3. Return dynamic data [cite: 228]
        return DashboardData(
            current_power_usage=power_usage,
            temperature_avg=round(avg_temp, 1),
            active_alerts_count=0, # You would fetch alerts here next
            forecast_summary="Fetching forecasts..." # You would fetch forecasts here next
        )

    async def get_system_alerts(self, user_token: str) -> List[Alert]:
        return [Alert(alert_id="1", severity="Critical", message="Sensor timeout", timestamp="2025-10-12")]

# --- FASTAPI ROUTER ---
router = APIRouter(prefix="/api/v1/gateway", tags=["AAC Gateway"])

async def get_aac_service():
    # INJECTION: Here we create the Mock and pass it to the service
    mock_db = MockMeasurementRepository()
    return AACImplementation(measurement_provider=mock_db)

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(token: str, service: IAccessControlAndCommunication = Depends(get_aac_service)):
    return await service.get_dashboard_view(token)