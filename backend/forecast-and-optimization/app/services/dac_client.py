"""
DAC HTTP Client

HTTP client implementation of DAC interfaces.
Communicates with the Data Access and Control module via REST API.

Team: Daniyar Zhumatayev & Kuzma Martysiuk
"""

import httpx
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.schemas.dac_interfaces import (
    IMeasurement,
    IForecastRead,
    IForecastWrite,
    ICoreDb,
    Measurement,
    ForecastData,
    BuildingMetadata,
    DeviceMetadata
)


class DACHttpClient(IMeasurement, IForecastRead, IForecastWrite, ICoreDb):
    """
    HTTP client that implements all DAC interfaces by calling the DAC REST API.
    
    This allows the Forecast module to consume real data from the database
    without any direct database access. All data flows through the DAC module.
    
    Usage:
        client = DACHttpClient("http://localhost:8001/api/v1")
        measurements = await client.get_measurements(...)
    """
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize DAC HTTP client.
        
        Args:
            base_url: Base URL of DAC REST API (e.g., "http://localhost:8001/api/v1")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        """Close the HTTP client connection."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    # =========================================================================
    # IMeasurement Interface Implementation
    # =========================================================================
    
    async def get_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        device_ids: Optional[List[str]] = None
    ) -> List[Measurement]:
        """
        Get historical measurements from DAC.
        
        Calls: GET /measurements
        """
        params = {
            "building_id": building_id,
            "metric_type": metric_type,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        if device_ids:
            params["device_ids"] = device_ids
        
        try:
            response = await self.client.get(
                f"{self.base_url}/measurements",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return [
                Measurement(
                    id=item.get("id", ""),
                    device_id=item.get("device_id", ""),
                    metric=item.get("metric", ""),
                    value=item.get("value", 0.0),
                    timestamp=datetime.fromisoformat(item["timestamp"]) if isinstance(item.get("timestamp"), str) else item.get("timestamp"),
                    tags=item.get("tags")
                )
                for item in data
            ]
        except httpx.HTTPStatusError as e:
            print(f"❌ DAC API error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"Failed to fetch measurements: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"❌ DAC connection error: {str(e)}")
            raise ConnectionError(f"Cannot connect to DAC service: {str(e)}")
    
    async def get_aggregated_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        aggregation: str = "1H"
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated measurements.
        
        Note: DAC does not currently expose this endpoint.
        Falls back to returning empty list.
        """
        # TODO: Request this endpoint from DAC team if needed
        print(f"⚠️  get_aggregated_measurements not implemented in DAC, returning empty")
        return []
    
    # =========================================================================
    # IForecastRead Interface Implementation
    # =========================================================================
    
    async def get_latest_forecast(
        self,
        building_id: str,
        forecast_type: str,
        horizon: str
    ) -> Optional[ForecastData]:
        """
        Get the most recent forecast for a building.
        
        Calls: GET /forecasts/latest
        """
        params = {
            "building_id": building_id,
            "forecast_type": forecast_type,
            "horizon": horizon
        }
        
        try:
            response = await self.client.get(
                f"{self.base_url}/forecasts/latest",
                params=params
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
            
            return self._parse_forecast_data(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise ValueError(f"Failed to fetch latest forecast: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Cannot connect to DAC service: {str(e)}")
    
    async def get_forecast_by_id(
        self,
        forecast_id: str
    ) -> Optional[ForecastData]:
        """
        Get a specific forecast by ID.
        
        Calls: GET /forecasts/{forecast_id}
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/forecasts/{forecast_id}"
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
            
            return self._parse_forecast_data(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise ValueError(f"Failed to fetch forecast: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Cannot connect to DAC service: {str(e)}")
    
    async def get_forecasts_in_range(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime,
        forecast_type: Optional[str] = None
    ) -> List[ForecastData]:
        """
        Get all forecasts within a date range.
        
        Note: DAC does not currently expose this endpoint.
        Falls back to returning empty list.
        """
        # TODO: Request this endpoint from DAC team if needed
        print(f"⚠️  get_forecasts_in_range not implemented in DAC, returning empty")
        return []
    
    def _parse_forecast_data(self, data: Dict[str, Any]) -> ForecastData:
        """Parse JSON response to ForecastData model."""
        if(data is None):
            return None
        valid_for = data.get("valid_for", {})
        
        
        # Handle datetime parsing for valid_for
        if isinstance(valid_for.get("from"), str):
            valid_for["from"] = datetime.fromisoformat(valid_for["from"].replace("Z", "+00:00"))
        if isinstance(valid_for.get("to"), str):
            valid_for["to"] = datetime.fromisoformat(valid_for["to"].replace("Z", "+00:00"))
        
        return ForecastData(
            id=data.get("id", ""),
            type=data.get("type", ""),
            horizon=data.get("horizon", ""),
            issued_at=datetime.fromisoformat(data["issued_at"].replace("Z", "+00:00")) if isinstance(data.get("issued_at"), str) else data.get("issued_at"),
            requested_by=data.get("requested_by", ""),
            series_item=data.get("series_item", []),
            valid_for=valid_for,
            model_meta=data.get("model_meta", {}),
            scope=data.get("scope")
        )
    
    # =========================================================================
    # IForecastWrite Interface Implementation
    # =========================================================================
    
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
        """
        Create a new forecast in DAC.
        
        Calls: POST /forecasts
        """
        # Serialize datetime objects in series_data
        serialized_series = []
        for item in series_data:
            serialized_item = {}
            for key, value in item.items():
                if isinstance(value, datetime):
                    serialized_item[key] = value.isoformat()
                else:
                    serialized_item[key] = value
            serialized_series.append(serialized_item)
        
        payload = {
            "forecast_type": forecast_type,
            "horizon": horizon,
            "building_id": building_id,
            "requested_by": requested_by,
            "series_data": serialized_series,
            "valid_from": valid_from.isoformat(),
            "valid_to": valid_to.isoformat(),
            "model_algorithm": model_algorithm,
            "model_version": model_version,
            "room_id": room_id,
            "floor_id": floor_id
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/forecasts",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            forecast_id = data.get("id", "")
            print(f"✅ DAC: Created forecast {forecast_id} for building {building_id}")
            return forecast_id
        except httpx.HTTPStatusError as e:
            print(f"❌ DAC API error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"Failed to create forecast: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Cannot connect to DAC service: {str(e)}")
    
    async def update_forecast(
        self,
        forecast_id: str,
        series_data: List[Dict[str, Any]]
    ) -> bool:
        """
        Update an existing forecast.
        
        Note: DAC does not currently expose this endpoint.
        Returns False as fallback.
        """
        # TODO: Request this endpoint from DAC team if needed
        print(f"⚠️  update_forecast not implemented in DAC, returning False")
        return False
    
    # =========================================================================
    # ICoreDb Interface Implementation
    # =========================================================================
    
    async def get_building(
        self,
        building_id: str
    ) -> Optional[BuildingMetadata]:
        """
        Get building metadata.
        
        Calls: GET /core/building/{building_id}
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/core/building/{building_id}"
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
            
            return BuildingMetadata(
                id=data.get("id", building_id),
                name=data.get("name", ""),
                address=data.get("address"),
                timezone=data.get("timezone", "UTC"),
                capacity_kw=data.get("capacity_kw")
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise ValueError(f"Failed to fetch building: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Cannot connect to DAC service: {str(e)}")
    
    async def get_devices(
        self,
        building_id: str,
        device_type: Optional[str] = None,
        status: Optional[str] = "active"
    ) -> List[DeviceMetadata]:
        """
        Get devices in a building.
        
        Calls: GET /core/devices
        """
        params = {"building_id": building_id}
        if device_type:
            params["device_type"] = device_type
        if status:
            params["status"] = status
        
        try:
            response = await self.client.get(
                f"{self.base_url}/core/devices",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return [
                DeviceMetadata(
                    id=item.get("id", ""),
                    device_id=item.get("device_id", ""),
                    type=item.get("type", ""),
                    building_id=building_id,
                    room_id=item.get("room_id"),
                    status=item.get("status", "active")
                )
                for item in data
            ]
        except httpx.HTTPStatusError as e:
            print(f"❌ DAC API error: {e.response.status_code}")
            return []
        except httpx.RequestError as e:
            print(f"❌ DAC connection error: {str(e)}")
            return []
    
    async def get_device(
        self,
        device_id: str
    ) -> Optional[DeviceMetadata]:
        """
        Get a specific device.
        
        Note: DAC does not expose single device endpoint.
        Returns None as fallback.
        """
        # TODO: Request this endpoint from DAC team if needed
        print(f"⚠️  get_device by ID not implemented in DAC, returning None")
        return None
