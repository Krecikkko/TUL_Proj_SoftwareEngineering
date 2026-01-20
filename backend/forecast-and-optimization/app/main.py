"""
Main FastAPI Application - Forecast and Optimization Module

Team: Daniyar Zhumatayev & Kuzma Martysiuk
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings
from app.schemas.dac_interfaces import MockDAC
from app.services.dac_client import DACHttpClient
from app.services.forecast_service import ForecastService
from app.api import routes

#Create FastAPI app
app = FastAPI(
    title="EMSIB Forecast & Optimization Service",
    description="ML-powered energy forecasting and cost optimization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DAC based on configuration
# Production: uses HTTP client to call DAC REST API
# Development: uses MockDAC with synthetic data
if settings.use_mock_dac:
    print("⚠️  Using MockDAC (development mode)", flush=True)
    mock_dac = MockDAC()
    measurement_provider = mock_dac.measurement
    forecast_read_provider = mock_dac.forecast_read
    forecast_write_provider = mock_dac.forecast_write
    core_db_provider = mock_dac.core_db
else:
    print(f"🔗 Connecting to DAC at {settings.dac_base_url}", flush=True)
    dac_client = DACHttpClient(
        base_url=settings.dac_base_url,
        timeout=settings.dac_timeout_seconds
    )
    measurement_provider = dac_client
    forecast_read_provider = dac_client
    forecast_write_provider = dac_client
    core_db_provider = dac_client

#Initialize ForecastService with DAC providers
forecast_service = ForecastService(
    measurement=measurement_provider,
    forecast_read=forecast_read_provider,
    forecast_write=forecast_write_provider,
    core_db=core_db_provider
)

#Inject service into routes
routes.set_forecast_service(forecast_service)

#Include router
app.include_router(routes.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "EMSIB Forecast & Optimization",
        "version": "1.0.0",
        "status": "running",
        "team": "Daniyar Zhumatayev & Kuzma Martysiuk",
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    print("\n" + "="*70)
    print("🚀 Forecast & Optimization Service Starting...")
    print("="*70)
    print(f"📅 Started: {datetime.utcnow().isoformat()}")
    print(f"👥 Team: Daniyar Zhumatayev & Kuzma Martysiuk")
    print(f"📖 Docs: http://localhost:8000/docs")
    print("="*70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    print("\n🛑 Service shutting down...\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
