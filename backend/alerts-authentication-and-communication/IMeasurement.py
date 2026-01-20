from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta
import random
import httpx 
from fastapi import HTTPException
from DataModels4DAC import Measurement
from vars import DAC_LOCALHOST

class IMeasurement(ABC):
    @abstractmethod
    async def get_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        device_ids: Optional[List[str]] = None
    ) -> List[Measurement]: pass


class MeasurementRepository(IMeasurement):
    async def get_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        device_ids: Optional[List[str]] = None
    ) -> List[Measurement]:
        # Implementacja rzeczywista pobierająca dane z bazy danych
        params = {
            "building_id": building_id,
            "metric_type": metric_type,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        if device_ids:
            extra = [("device_ids", d) for d in device_ids]
        else:
            extra = []

        url = f"{DAC_LOCALHOST}/measurements"
        async with httpx.AsyncClient() as client:
            try: 
                resp = await client.get(url, params=[*params.items(), *extra])
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"DAC connection error: {str(e)}")
            
        return [Measurement(
            id = item["id"],
            device_id = item["device_id"],
            metric = item["metric"],
            value = item["value"],
            timestamp= item["timestamp"],
            tags = item.get("tags", None)
        ) for item in resp.json()]



class MockMeasurementRepository(IMeasurement):
    async def get_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        device_ids: Optional[List[str]] = None
    ) -> List[Measurement]:
        
        readings = []
        for i in range(5):
            ts = end_date - timedelta(minutes=i*10)
            val = 0.0
            
            if metric_type == "power_w": val = random.uniform(4000, 6000)
            elif metric_type == "temp_c": val = random.uniform(20.0, 30.0)
            elif metric_type == "co2_ppm": val = random.uniform(400, 1200)
            elif metric_type == "humidity_pct": val = random.uniform(30, 60)

            readings.append(Measurement(
                id=f"m_{i}", 
                device_id="dev_mock_1", 
                metric=metric_type, 
                value=val, 
                timestamp=ts,
                tags={"room": "Room-101"}
            ))

        return readings