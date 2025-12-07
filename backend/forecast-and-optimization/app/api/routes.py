"""
API Routes for Forecast & Optimization Module
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import Optional

from app.schemas.forecast_service import (
    ForecastRequest,
    ForecastResult,
    OptimizationRequest,
    OptimizationResult,
    ModelPerformanceMetrics,
    InsufficientDataError,
    ModelNotTrainedError
)

#Router instance
router = APIRouter()

#forecast_service will be injected by main.py
forecast_service = None


def set_forecast_service(service):
    """Set the forecast service instance"""
    global forecast_service
    forecast_service = service


@router.post("/forecast", response_model=ForecastResult, tags=["Forecast"])
async def request_forecast(request: ForecastRequest):
    """Generate energy consumption or cost forecast"""
    try:
        result = await forecast_service.request_forecast(request)
        return result
    except InsufficientDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast generation failed: {str(e)}"
        )


@router.get("/forecast/{forecast_id}", response_model=ForecastResult, tags=["Forecast"])
async def get_forecast(forecast_id: str, requested_by: str):
    """Retrieve existing forecast by ID"""
    result = await forecast_service.get_forecast(forecast_id, requested_by)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Forecast {forecast_id} not found"
        )
    return result


@router.get("/forecast/latest/{building_id}", response_model=Optional[ForecastResult], tags=["Forecast"])
async def get_latest_forecast(
    building_id: str,
    forecast_type: str = "energy_demand",
    horizon: str = "24H",
    requested_by: str = "system"
):
    """Get most recent forecast for a building"""
    result = await forecast_service.get_latest_forecast(
        building_id=building_id,
        forecast_type=forecast_type,
        horizon=horizon,
        requested_by=requested_by
    )
    return result


@router.post("/optimization", response_model=OptimizationResult, tags=["Optimization"])
async def get_optimization(request: OptimizationRequest):
    """Generate cost optimization recommendations"""
    try:
        result = await forecast_service.get_optimization(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )


@router.post("/model/train", tags=["Model Management"])
async def train_model(
    building_id: str,
    model_type: str,
    start_date: datetime,
    end_date: datetime,
    requested_by: str
):
    """Train or retrain ML model for a building"""
    try:
        result = await forecast_service.train_model(
            building_id=building_id,
            model_type=model_type,
            start_date=start_date,
            end_date=end_date,
            requested_by=requested_by
        )
        return result
    except InsufficientDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )


@router.get("/model/performance", response_model=ModelPerformanceMetrics, tags=["Model Management"])
async def get_model_performance(building_id: str, model_type: str, requested_by: str):
    """Get performance metrics for a building's ML model"""
    try:
        result = await forecast_service.get_model_performance(
            building_id=building_id,
            model_type=model_type,
            requested_by=requested_by
        )
        return result
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model performance: {str(e)}"
        )


@router.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return await forecast_service.health_check()
