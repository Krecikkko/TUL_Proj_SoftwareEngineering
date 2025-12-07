"""
DAC (Data Access and Control) Interfaces

These are the interfaces we EXPECT from the DAC team.
Based on the database schemas from the architecture presentation.

Team: Maja Morawiec & Lena Schilling (DAC team will implement these)
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# ============================================================================
# DATA MODELS (based on database schemas from presentation)
# ============================================================================

class Measurement(BaseModel):
    """
    Based on MEASUREMENTS table in MetricsDb (MongoDB)
    
    Schema from presentation:
    - _id: string
    - deviceId: string
    - metric: string (power_w | temp_c | humidity_pct | co2_ppm)
    - value: double
    - ts: datetime
    - tags: object (e.g., {room: 'A-101'})
    """
    id: str
    device_id: str
    metric: str  # "power_w", "temp_c", "humidity_pct", "co2_ppm"
    value: float
    timestamp: datetime
    tags: Optional[Dict[str, Any]] = None


class ForecastData(BaseModel):
    """
    Based on FORECASTS table in ForecastDb (MongoDB)
    
    Schema from presentation:
    - id: string (ObjectId)
    - type: string (energy_demand | price | temp_setpoint)
    - horizon: string (ISO-8601: 1H/8H/1D/7D/1M/1Y)
    - issuedAt: datetime (UTC)
    - requested_by: UUID (requester_id)
    - series_item: [{ts: datetime, value: double, conf: 0..1}]
    - valid_for: {from: datetime, to: datetime}
    - model_meta: {algo: string, ver: string}
    - scope: {buildingId: UUID, roomId: UUID, floorId: UUID} (optional)
    """
    id: str
    type: str  # "energy_demand", "price", "temp_setpoint"
    horizon: str  # "1H", "8H", "1D", "7D", "1M", "1Y"
    issued_at: datetime
    requested_by: str
    series_item: List[Dict[str, Any]]  # [{ts, value, conf}, ...]
    valid_for: Dict[str, datetime]  # {from, to}
    model_meta: Dict[str, str]  # {algo, ver}
    scope: Optional[Dict[str, str]] = None  # {buildingId, roomId, floorId}


class BuildingMetadata(BaseModel):
    """
    Based on CoreDb schema (PostgreSQL)
    Building metadata needed for forecasting
    """
    id: str
    name: str
    address: Optional[str] = None
    timezone: Optional[str] = "UTC"
    capacity_kw: Optional[float] = None  # Electrical capacity


class DeviceMetadata(BaseModel):
    """
    Based on CoreDb schema (PostgreSQL)
    Device metadata needed for forecasting
    """
    id: str
    device_id: str
    type: str  # "sensor", "hvac", "lighting", etc.
    building_id: str
    room_id: Optional[str] = None
    status: str  # "active", "inactive", "maintenance"


# ============================================================================
# INTERFACES WE REQUIRE FROM DAC
# ============================================================================

class IMeasurement(ABC):
    """
    Interface for retrieving historical measurement data from MetricsDb.
    
    DAC team will implement this to provide us with sensor readings
    for ML model training and forecasting.
    """
    
    @abstractmethod
    async def get_measurements(
        self,
        building_id: str,
        metric_type: str,  # "power_w", "temp_c", etc.
        start_date: datetime,
        end_date: datetime,
        device_ids: Optional[List[str]] = None
    ) -> List[Measurement]:
        """
        Get historical measurements for ML training.
        
        Args:
            building_id: Building identifier
            metric_type: Type of metric (power_w, temp_c, humidity_pct, co2_ppm)
            start_date: Start of time range
            end_date: End of time range
            device_ids: Optional list of specific devices (if None, all devices)
            
        Returns:
            List of measurements ordered by timestamp
            
        Raises:
            ValueError: If date range invalid or building not found
            PermissionError: If user lacks access to building data
        """
        pass
    
    @abstractmethod
    async def get_aggregated_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        aggregation: str = "1H"  # "1H", "1D", etc.
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated measurements (for efficiency with large datasets).
        
        Args:
            building_id: Building identifier
            metric_type: Type of metric
            start_date: Start of time range
            end_date: End of time range
            aggregation: Aggregation period (e.g., "1H" for hourly)
            
        Returns:
            List of {timestamp, avg, min, max, count} dicts
        """
        pass


class IForecastRead(ABC):
    """
    Interface for reading existing forecasts from ForecastDb.
    
    Needed for:
    - Optimization engine to get latest energy forecasts
    - Checking if recent forecast exists before generating new one
    - Retrieving forecast history for accuracy tracking
    """
    
    @abstractmethod
    async def get_latest_forecast(
        self,
        building_id: str,
        forecast_type: str,  # "energy_demand", "price", "temp_setpoint"
        horizon: str  # "1H", "24H", "7D"
    ) -> Optional[ForecastData]:
        """
        Get the most recent forecast for a building.
        
        Args:
            building_id: Building identifier
            forecast_type: Type of forecast
            horizon: Forecast horizon
            
        Returns:
            Latest forecast or None if no recent forecast exists
        """
        pass
    
    @abstractmethod
    async def get_forecast_by_id(
        self,
        forecast_id: str
    ) -> Optional[ForecastData]:
        """
        Get a specific forecast by ID.
        
        Args:
            forecast_id: Forecast identifier
            
        Returns:
            Forecast data or None if not found
        """
        pass
    
    @abstractmethod
    async def get_forecasts_in_range(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime,
        forecast_type: Optional[str] = None
    ) -> List[ForecastData]:
        """
        Get all forecasts within a date range (for history/accuracy tracking).
        
        Args:
            building_id: Building identifier
            start_date: Start of range
            end_date: End of range
            forecast_type: Optional filter by type
            
        Returns:
            List of forecasts
        """
        pass


class IForecastWrite(ABC):
    """
    Interface for writing new forecasts to ForecastDb.
    
    Our module will use this to store generated forecasts.
    """
    
    @abstractmethod
    async def create_forecast(
        self,
        forecast_type: str,
        horizon: str,
        building_id: str,
        requested_by: str,
        series_data: List[Dict[str, Any]],  # [{ts, value, conf}, ...]
        valid_from: datetime,
        valid_to: datetime,
        model_algorithm: str,  # "LSTM", "XGBoost", etc.
        model_version: str,
        room_id: Optional[str] = None,
        floor_id: Optional[str] = None
    ) -> str:
        """
        Create a new forecast in ForecastDb.
        
        Args:
            forecast_type: "energy_demand", "price", or "temp_setpoint"
            horizon: "1H", "8H", "1D", "7D", etc.
            building_id: Building identifier
            requested_by: User ID who requested forecast
            series_data: List of {ts: datetime, value: float, conf: float}
            valid_from: Start of forecast validity
            valid_to: End of forecast validity
            model_algorithm: ML algorithm used (e.g., "LSTM", "XGBoost")
            model_version: Model version (e.g., "1.4.2")
            room_id: Optional room scope
            floor_id: Optional floor scope
            
        Returns:
            forecast_id: ID of created forecast
            
        Raises:
            ValueError: If data validation fails
            PermissionError: If user lacks write permission
        """
        pass
    
    @abstractmethod
    async def update_forecast(
        self,
        forecast_id: str,
        series_data: List[Dict[str, Any]]
    ) -> bool:
        """
        Update an existing forecast (rarely used - usually create new).
        
        Args:
            forecast_id: Forecast to update
            series_data: New series data
            
        Returns:
            True if successful
        """
        pass


class ICoreDb(ABC):
    """
    Interface for accessing building and device metadata from CoreDb.
    
    Needed for:
    - Getting building electrical capacity (for validation)
    - Getting device information
    - Timezone conversion
    """
    
    @abstractmethod
    async def get_building(
        self,
        building_id: str
    ) -> Optional[BuildingMetadata]:
        """
        Get building metadata.
        
        Args:
            building_id: Building identifier
            
        Returns:
            Building metadata or None if not found
        """
        pass
    
    @abstractmethod
    async def get_devices(
        self,
        building_id: str,
        device_type: Optional[str] = None,
        status: Optional[str] = "active"
    ) -> List[DeviceMetadata]:
        """
        Get devices in a building.
        
        Args:
            building_id: Building identifier
            device_type: Optional filter by type
            status: Optional filter by status (default: "active")
            
        Returns:
            List of devices
        """
        pass
    
    @abstractmethod
    async def get_device(
        self,
        device_id: str
    ) -> Optional[DeviceMetadata]:
        """
        Get a specific device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device metadata or None if not found
        """
        pass


# ============================================================================
# MOCK IMPLEMENTATIONS (for development without DAC)
# ============================================================================

class MockDAC:
    """
    Mock implementation of all DAC interfaces.
    We use this for development until DAC team provides real implementation.
    """
    
    def __init__(self):
        self.measurement = MockMeasurement()
        self.forecast_read = MockForecastRead()
        self.forecast_write = MockForecastWrite()
        self.core_db = MockCoreDb()


class MockMeasurement(IMeasurement):
    """Mock implementation returning fake sensor data"""
    
    async def get_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        device_ids: Optional[List[str]] = None
    ) -> List[Measurement]:
        """Return mock measurement data"""
        import numpy as np
        from datetime import timedelta
        
        measurements = []
        current = start_date
        
        # Generate hourly measurements
        while current <= end_date:
            # Realistic patterns based on metric type
            if metric_type == "power_w":
                # Power: higher during day, lower at night
                hour = current.hour
                base = 50000 if 8 <= hour <= 18 else 30000
                value = base + np.random.normal(0, 5000)
            elif metric_type == "temp_c":
                # Temperature: 20-24°C
                value = 22 + np.random.normal(0, 1)
            elif metric_type == "humidity_pct":
                # Humidity: 40-60%
                value = 50 + np.random.normal(0, 5)
            else:  # co2_ppm
                # CO2: 400-800 ppm
                value = 600 + np.random.normal(0, 100)
            
            measurements.append(Measurement(
                id=f"m_{current.timestamp()}",
                device_id=f"device_{building_id}_001",
                metric=metric_type,
                value=max(0, value),  # Ensure non-negative
                timestamp=current,
                tags={"room": "A-101", "floor": "1"}
            ))
            
            current += timedelta(hours=1)
        
        return measurements
    
    async def get_aggregated_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        aggregation: str = "1H"
    ) -> List[Dict[str, Any]]:
        """Return mock aggregated data"""
        measurements = await self.get_measurements(
            building_id, metric_type, start_date, end_date
        )
        
        # Simple aggregation (in real impl, DAC does this efficiently)
        return [
            {
                "timestamp": m.timestamp,
                "avg": m.value,
                "min": m.value * 0.9,
                "max": m.value * 1.1,
                "count": 1
            }
            for m in measurements
        ]


class MockForecastRead(IForecastRead):
    """Mock implementation returning fake forecasts"""
    
    def __init__(self):
        self.forecasts: Dict[str, ForecastData] = {}
    
    async def get_latest_forecast(
        self,
        building_id: str,
        forecast_type: str,
        horizon: str
    ) -> Optional[ForecastData]:
        """Return most recent mock forecast"""
        # In mock, return None (no existing forecast)
        return None
    
    async def get_forecast_by_id(
        self,
        forecast_id: str
    ) -> Optional[ForecastData]:
        """Get forecast by ID"""
        return self.forecasts.get(forecast_id)
    
    async def get_forecasts_in_range(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime,
        forecast_type: Optional[str] = None
    ) -> List[ForecastData]:
        """Get forecasts in range"""
        return []  # No historical forecasts in mock


class MockForecastWrite(IForecastWrite):
    """Mock implementation for writing forecasts"""
    
    def __init__(self):
        self.forecasts: Dict[str, ForecastData] = {}
        self.next_id = 1
    
    async def create_forecast(
        self,
        forecast_type: str,
        horizon: str,
        building_id: str,
        requested_by: str,
        series_data: List[Dict[str, Any]],
        valid_from: datetime,
        valid_to: datetime,
        model_algorithm: str,
        model_version: str,
        room_id: Optional[str] = None,
        floor_id: Optional[str] = None
    ) -> str:
        """Create mock forecast and store in memory"""
        forecast_id = f"forecast_{self.next_id}"
        self.next_id += 1
        
        scope = {"buildingId": building_id}
        if room_id:
            scope["roomId"] = room_id
        if floor_id:
            scope["floorId"] = floor_id
        
        forecast = ForecastData(
            id=forecast_id,
            type=forecast_type,
            horizon=horizon,
            issued_at=datetime.utcnow(),
            requested_by=requested_by,
            series_item=series_data,
            valid_for={"from": valid_from, "to": valid_to},
            model_meta={"algo": model_algorithm, "ver": model_version},
            scope=scope
        )
        
        self.forecasts[forecast_id] = forecast
        print(f"✅ Mock: Created forecast {forecast_id} for building {building_id}")
        return forecast_id
    
    async def update_forecast(
        self,
        forecast_id: str,
        series_data: List[Dict[str, Any]]
    ) -> bool:
        """Update mock forecast"""
        if forecast_id in self.forecasts:
            self.forecasts[forecast_id].series_item = series_data
            return True
        return False


class MockCoreDb(ICoreDb):
    """Mock implementation for building/device metadata"""
    
    async def get_building(
        self,
        building_id: str
    ) -> Optional[BuildingMetadata]:
        """Return mock building metadata"""
        return BuildingMetadata(
            id=building_id,
            name=f"Building {building_id}",
            address="123 University St, Łódź, Poland",
            timezone="Europe/Warsaw",
            capacity_kw=500.0  # 500 kW capacity
        )
    
    async def get_devices(
        self,
        building_id: str,
        device_type: Optional[str] = None,
        status: Optional[str] = "active"
    ) -> List[DeviceMetadata]:
        """Return mock devices"""
        return [
            DeviceMetadata(
                id="dev_001",
                device_id=f"device_{building_id}_001",
                type="power_meter",
                building_id=building_id,
                room_id="A-101",
                status="active"
            ),
            DeviceMetadata(
                id="dev_002",
                device_id=f"device_{building_id}_002",
                type="temp_sensor",
                building_id=building_id,
                room_id="A-102",
                status="active"
            )
        ]
    
    async def get_device(
        self,
        device_id: str
    ) -> Optional[DeviceMetadata]:
        """Return mock device"""
        return DeviceMetadata(
            id=device_id,
            device_id=device_id,
            type="power_meter",
            building_id="B001",
            room_id="A-101",
            status="active"
        )
