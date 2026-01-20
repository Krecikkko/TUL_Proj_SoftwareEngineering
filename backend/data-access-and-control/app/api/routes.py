from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.repositories.dac_repository import DataAccessGateway, MeasurementSchema, ForecastData
from pydantic import BaseModel

router = APIRouter()
gateway = DataAccessGateway()

class ForecastCreateRequest(BaseModel):
    forecast_type: str
    horizon: str
    building_id: str
    requested_by: str
    series_data: List[Dict[str, Any]]
    valid_from: datetime
    valid_to: datetime
    model_algorithm: str
    model_version: str
    room_id: Optional[str] = None
    floor_id: Optional[str] = None

@router.get("/measurements", response_model=List[MeasurementSchema])
async def get_measurements(
    building_id: str,
    metric_type: str,
    start_date: datetime,
    end_date: datetime,
    device_ids: Optional[List[str]] = Query(None)
):
    try:
        results = await gateway.get_measurements(
            building_id=building_id,
            metric_type=metric_type,
            start_date=start_date,
            end_date=end_date,
            device_ids=device_ids
        )
        return results
    except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=repr(e))
    
@router.post("/forecasts", status_code=201)
async def create_forecast(req: ForecastCreateRequest):
    try:
        forecast_id = await gateway.create_forecast(
            forecast_type=req.forecast_type,
            horizon=req.horizon,
            building_id=req.building_id,
            requested_by=req.requested_by,
            series_data=req.series_data,
            valid_from=req.valid_from,
            valid_to=req.valid_to,
            model_algorithm=req.model_algorithm, 
            model_version=req.model_version,
            room_id=req.room_id, 
            floor_id=req.floor_id
        )
        return {"id": forecast_id, "message": "Forecast created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/forecasts/latest", response_model=Optional[ForecastData])
async def get_latest_forecast(
    building_id: str,
    forecast_type: str, 
    horizon: str
):
    result = await gateway.get_latest_forecast(
        building_id=building_id,
        forecast_type=forecast_type,
        horizon=horizon
    )
    return result

@router.get("/forecasts/{forecast_id}", response_model=Optional[ForecastData])
async def get_forecast_by_id(forecast_id: str):
    result = await gateway.get_forecast_by_id(forecast_id)
    if not result:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return result 

@router.get("/core/devices")
async def get_devices(building_id: str): 
    return await gateway.get_devices(building_id)

@router.get("/core/building/{building_id}")
async def get_building(building_id: str):
    res = await gateway.get_building(building_id)
    if not res:
        raise HTTPException(status_code=404, detail="Building not found")
    return res