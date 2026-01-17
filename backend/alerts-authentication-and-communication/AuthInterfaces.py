from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from jose import JWTError, jwt  

from IMeasurement import IMeasurement, MockMeasurementRepository
from ICoreDb import ICoreDb, MockCoreDb
from IForecastRead import IForecastRead, MockForecastRepository
from DataModels4DAC import (
    UserRole, Alert, AlertSeverity, Measurement, 
    MeasurementResponse, ForecastResponse, Forecast, User
)

SECRET_KEY = "my_super_secure_secret_key_for_emsib_project"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/gateway/login")

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

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class IAccessControlAndCommunication(ABC):
    @abstractmethod
    async def login_user(self, credentials: UserLogin) -> AuthToken: pass
 
    @abstractmethod
    async def get_dashboard_view(self, current_user: User, buildingId: str) -> DashboardData: pass
    
    @abstractmethod
    async def get_system_alerts(
        self, current_user: User, buildingId: str, fromDate: datetime, toDate: datetime
    ) -> List[Alert]: pass
    
    @abstractmethod
    async def get_measurements_view(
        self, buildingId: str, metric: str, fromDate: datetime, toDate: datetime, deviceId: Optional[str] = None
    ) -> List[MeasurementResponse]: pass

    @abstractmethod
    async def get_forecasts_view(
        self, buildingId: str, type: str, fromDate: datetime, toDate: datetime
    ) -> List[ForecastResponse]: pass

class AACImplementation(IAccessControlAndCommunication):
    
    def __init__(self, measurement_db, core_db, forecast_db):
        self.meas_db = measurement_db
        self.core_db = core_db
        self.fore_db = forecast_db

    async def login_user(self, credentials: UserLogin) -> AuthToken:
        user = await self.core_db.get_user_by_username(credentials.username)
   
        if not user or credentials.password != user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return AuthToken(
            access_token=access_token, 
            token_type="bearer", 
            role=user.role.value
        )

    async def get_dashboard_view(self, current_user: User, buildingId: str) -> DashboardData:
        
        end = datetime.utcnow()
        start = end - timedelta(hours=24)
        
        power_metrics = await self.meas_db.get_measurements(buildingId, "power_w", start, end)
        current_power = sum(m.value for m in power_metrics)
        
        temp_metrics = await self.meas_db.get_measurements(buildingId, "temp_c", start, end)
        avg_temp = sum(m.value for m in temp_metrics) / len(temp_metrics) if temp_metrics else 0.0

        forecast = await self.fore_db.get_latest_forecast(buildingId, "energy_demand", "1D")
        summary = "No data"
        if forecast and forecast.series_item:
            val = int(forecast.series_item[0]["value"])
            summary = f"Demand expected to reach {val} kW."
            
        alerts = await self.get_system_alerts(current_user, buildingId, start, end)
        
        return DashboardData(
            current_power_usage=round(current_power, 2),
            temperature_avg=round(avg_temp, 1),
            active_alerts_count=len(alerts),
            forecast_summary=summary
        )

    async def get_system_alerts(
        self, current_user: User, buildingId: str, fromDate: datetime, toDate: datetime
    ) -> List[Alert]:
        
        generated_alerts = []
        temps = await self.meas_db.get_measurements(buildingId, "temp_c", fromDate, toDate)
        for m in temps:
            if m.value > 28.0:
                generated_alerts.append(Alert(
                    id=f"alert_{m.id}",
                    building_id=buildingId,
                    severity=AlertSeverity.MEDIUM,
                    message=f"High Temperature: {m.value}°C",
                    device_id=m.device_id,
                    timestamp=m.timestamp
                ))
        co2s = await self.meas_db.get_measurements(buildingId, "co2_ppm", fromDate, toDate)
        for m in co2s:
            if m.value > 1000:
                generated_alerts.append(Alert(
                    id=f"alert_{m.id}",
                    building_id=buildingId,
                    severity=AlertSeverity.HIGH,
                    message=f"Poor Air Quality: {m.value} ppm",
                    device_id=m.device_id,
                    timestamp=m.timestamp
                ))
        return generated_alerts

    async def get_measurements_view(
        self, buildingId: str, metric: str, fromDate: datetime, toDate: datetime, deviceId: Optional[str] = None
    ) -> List[MeasurementResponse]:
        metric_map = { "temperature": "temp_c", "power": "power_w", "humidity": "humidity_pct", "co2": "co2_ppm" }
        dac_metric = metric_map.get(metric, metric)

        raw_data = await self.meas_db.get_measurements(
            building_id=buildingId, metric_type=dac_metric, start_date=fromDate, end_date=toDate, device_ids=[deviceId] if deviceId else None
        )

        return [MeasurementResponse(
            ts=r.timestamp, value=r.value, metric=metric, device_id=r.device_id, buildingId=buildingId
        ) for r in raw_data]

    async def get_forecasts_view(
        self, buildingId: str, type: str, fromDate: datetime, toDate: datetime
    ) -> List[ForecastResponse]:
        raw_forecasts = await self.fore_db.get_forecasts_in_range(
            building_id=buildingId,
            start_date=fromDate,
            end_date=toDate,
            forecast_type=type
        )
        response_list = []
        for f in raw_forecasts:
            response_list.append(ForecastResponse(
                buildingId=buildingId,
                type=f.type,
                horizon=f.horizon,
                series=f.series_item,
                algo=f.model_meta.get("algo")
            ))
        return response_list



async def get_aac_service():
    return AACImplementation(
        measurement_db=MockMeasurementRepository(),
        core_db=MockCoreDb(),
        forecast_db=MockForecastRepository()
    )

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    svc: AACImplementation = Depends(get_aac_service)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await svc.core_db.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

router = APIRouter(prefix="/api/v1/gateway", tags=["AAC Gateway"])

@router.post("/login")
async def login(creds: UserLogin, svc: IAccessControlAndCommunication = Depends(get_aac_service)):
    return await svc.login_user(creds)


@router.get("/dashboard")
async def dashboard(
    buildingId: str, 
    current_user: User = Depends(get_current_user), 
    svc: IAccessControlAndCommunication = Depends(get_aac_service)
):
    return await svc.get_dashboard_view(current_user, buildingId)

@router.get("/alerts")
async def alerts(
    buildingId: str, fromDate: datetime, toDate: datetime, 
    current_user: User = Depends(get_current_user),
    svc: IAccessControlAndCommunication = Depends(get_aac_service)
):
    return await svc.get_system_alerts(current_user, buildingId, fromDate, toDate)

@router.get("/measurements")
async def get_measurements(
    buildingId: str, metric: str, fromDate: datetime, toDate: datetime, deviceId: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    svc: IAccessControlAndCommunication = Depends(get_aac_service)
):
    return await svc.get_measurements_view(buildingId, metric, fromDate, toDate, deviceId)

@router.get("/forecasts")
async def get_forecasts(
    buildingId: str, type: str, fromDate: datetime, toDate: datetime,
    current_user: User = Depends(get_current_user),
    svc: IAccessControlAndCommunication = Depends(get_aac_service)
):
    return await svc.get_forecasts_view(buildingId, type, fromDate, toDate)