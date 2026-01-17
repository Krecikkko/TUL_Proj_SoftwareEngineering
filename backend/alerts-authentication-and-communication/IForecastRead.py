from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import random
from typing import List, Optional
from DataModels4DAC import Forecast

class IForecastRead(ABC):
    @abstractmethod
    async def get_latest_forecast(
        self, 
        building_id: str, 
        forecast_type: str, 
        horizon: str
    ) -> Optional[Forecast]: pass

    # NEW METHOD: Matches dac_repository.py signature
    @abstractmethod
    async def get_forecasts_in_range(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime,
        forecast_type: Optional[str] = None
    ) -> List[Forecast]: pass

class MockForecastRepository(IForecastRead):
    async def get_latest_forecast(
        self, 
        building_id: str, 
        forecast_type: str, 
        horizon: str
    ) -> Optional[Forecast]:
        # Reuse the generation logic
        return (await self.get_forecasts_in_range(building_id, datetime.utcnow(), datetime.utcnow(), forecast_type))[0]

    async def get_forecasts_in_range(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime,
        forecast_type: Optional[str] = None
    ) -> List[Forecast]:
        
        # Simulate finding 2 forecasts in the requested range
        results = []
        for i in range(2):
            issued_time = start_date + timedelta(days=i)
            
            # Generate dummy series data relative to issued_time
            series_data = []
            for h in range(24):
                series_data.append({
                    "ts": issued_time + timedelta(hours=h),
                    "value": random.uniform(2000, 4500),
                    "conf": 0.90
                })

            results.append(Forecast(
                id=f"fc_hist_{i}",
                type=forecast_type or "energy_demand",
                horizon="1D",
                issued_at=issued_time,
                requested_by="req_mock",
                series_item=series_data,
                valid_for={"from": issued_time, "to": issued_time + timedelta(days=1)},
                model_meta={"algo": "XGBoost", "ver": "2.0"},
                scope={"buildingId": building_id}
            ))
            
        return results