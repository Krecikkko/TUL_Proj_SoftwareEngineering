from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from http.client import HTTPException
import random
from typing import List, Optional
from DataModels4DAC import Forecast
from vars import DAC_LOCALHOST
import httpx 

class IForecastRead(ABC):
    @abstractmethod
    async def get_latest_forecast(
        self, 
        building_id: str, 
        forecast_type: str, 
        horizon: str
    ) -> Optional[Forecast]: pass

    @abstractmethod
    async def get_forecasts_in_range(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime,
        forecast_type: Optional[str] = None
    ) -> List[Forecast]: pass


class RealForecastRepository(IForecastRead):
    # async def get_latest_forecast(
    #     self, 
    #     building_id: str, 
    #     forecast_type: str, 
    #     horizon: str
    # ) -> Optional[Forecast]:
    #     # Niezaimplementowano przez DAC
    #     url=f"{DAC_LOCALHOST}/forecasts/latest"
    #     params = {
    #         "building_id": building_id,
    #         "forecast_type": forecast_type,
    #         "horizon": horizon
    #     }
    #     async with httpx.AsyncClient() as client:
    #         try:
    #             resp =  await client.get(url, params=params)
    #         except Exception as e:
    #             raise HTTPException(status_code=500, detail=f"DAC connection error: {str(e)}")
    #     item = resp.json()
    #     return Forecast(
    #         id=item["id"],
    #         type=item["type"],
    #         horizon=item["horizon"],
    #         issued_at=item["issued_at"],
    #         requested_by=item["requested_by"],
    #         series_item=item["series_item"],
    #         valid_for=item["valid_for"],
    #         model_meta=item["model_meta"],
    #         scope=item.get("scope", None)
    #     )
    pass

    async def get_forecasts_in_range(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime,
        forecast_type: Optional[str] = None
    ) -> List[Forecast]:
        # Niezaimplementowano przez DAC
        pass


class MockForecastRepository(IForecastRead):
    async def get_latest_forecast(
        self, 
        building_id: str, 
        forecast_type: str, 
        horizon: str
    ) -> Optional[Forecast]:
        return (await self.get_forecasts_in_range(building_id, datetime.utcnow(), datetime.utcnow(), forecast_type))[0]

    async def get_forecasts_in_range(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime,
        forecast_type: Optional[str] = None
    ) -> List[Forecast]:
        results = []
        for i in range(2):
            issued_time = start_date + timedelta(days=i)
            
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