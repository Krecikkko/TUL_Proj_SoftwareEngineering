"""
Main FastAPI Application - Forecast and Optimization Module

Team: Daniyar Zhumatayev & Kuzma Martysiuk
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.schemas.dac_interfaces import MockDAC
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

#Initialize DAC (Mock for now)
mock_dac = MockDAC()

#Initialize ForecastService
forecast_service = ForecastService(
    measurement=mock_dac.measurement,
    forecast_read=mock_dac.forecast_read,
    forecast_write=mock_dac.forecast_write,
    core_db=mock_dac.core_db
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
