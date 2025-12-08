"""
ForecastService - Main orchestrator implementing IForecastService

This is the main service that coordinates all components:
- ForecastEngine (for generating forecasts)
- OptimizationEngine (for generating recommendations)
- MLModelManager (for managing ML models)
- DAC interfaces (for data access)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.schemas.forecast_service import (
    IForecastService,
    ForecastRequest,
    ForecastResult,
    OptimizationRequest,
    OptimizationResult,
    OptimizationRecommendation,
    ModelPerformanceMetrics,
    InsufficientDataError,
    ModelNotTrainedError
)
from app.schemas.dac_interfaces import (
    IMeasurement,
    IForecastRead,
    IForecastWrite,
    ICoreDb
)
from app.services.forecast_engine import ForecastEngine
from app.services.optimization_engine import OptimizationEngine
from app.services.ml_model_manager import MLModelManager


class ForecastService(IForecastService):
    """
    Main Forecast and Optimization service implementation.
    
    Coordinates all components to provide forecasting and optimization
    capabilities to the EMSIB system.
    """
    
    def __init__(
        self,
        measurement: IMeasurement,
        forecast_read: IForecastRead,
        forecast_write: IForecastWrite,
        core_db: ICoreDb
    ):
        """
        Initialize ForecastService with DAC interfaces.
        
        Args:
            measurement: IMeasurement interface from DAC
            forecast_read: IForecastRead interface from DAC
            forecast_write: IForecastWrite interface from DAC
            core_db: ICoreDb interface from DAC
        """
        #Store DAC interfaces
        self.measurement = measurement
        self.forecast_read = forecast_read
        self.forecast_write = forecast_write
        self.core_db = core_db
        
        #Initialize engines (composition relationship from class diagram)
        self.model_manager = MLModelManager()
        self.forecast_engine = ForecastEngine(
            measurement_interface=measurement,
            model_manager=self.model_manager,
            accuracy_threshold=0.85  # 85% minimum accuracy
        )
        self.optimization_engine = OptimizationEngine()
        
        #Service metadata
        self.started_at = datetime.utcnow()
        
        print("🚀 ForecastService initialized")
    
    # ========================================================================
    # FORECAST GENERATION
    # ========================================================================
    
    async def request_forecast(
        self,
        request: ForecastRequest
    ) -> ForecastResult:
        """
        Generate forecast for a building.
        
        Implements FR1, FR2, FR6, FR8.
        """
        print(f"\n{'='*60}")
        print(f"📊 FORECAST REQUEST")
        print(f"{'='*60}")
        print(f"Building: {request.building_id}")
        print(f"Horizon: {request.horizon}")
        print(f"Type: {request.forecast_type}")
        print(f"Requested by: {request.requested_by}")
        
        #Step 1: Validate building exists
        building = await self.core_db.get_building(request.building_id)
        if not building:
            raise ValueError(f"Building {request.building_id} not found")
        
        #Step 2: Check for existing recent forecast (avoid redundant generation)
        existing = await self.forecast_read.get_latest_forecast(
            building_id=request.building_id,
            forecast_type=request.forecast_type,
            horizon=request.horizon
        )
        
        if existing:
            issued_at = existing.issued_at
            age_hours = (datetime.utcnow() - issued_at).total_seconds() / 3600
            
            if age_hours < 1.0:
                print(f"✅ Using existing forecast from {age_hours:.1f} hours ago")
                return self._convert_to_forecast_result(existing)
        
        #Step 3: Generate new forecast
        print(f"🔄 Generating new forecast...")
        
        try:
            forecast_values, accuracy, model_used = await self.forecast_engine.generate_forecast(
                building_id=request.building_id,
                horizon=request.horizon,
                forecast_type=request.forecast_type,
                model_type="auto"  # Auto-select LSTM or XGBoost
            )
        except InsufficientDataError as e:
            raise ValueError(f"Cannot generate forecast: {str(e)}")
        
        #Step 4: Calculate validity period
        now = datetime.utcnow()
        valid_from = now
        
        #Parse horizon to determine validity end
        if request.horizon.endswith('H'):
            hours = int(request.horizon[:-1])
            valid_to = now + timedelta(hours=hours)
        elif request.horizon.endswith('D'):
            days = int(request.horizon[:-1])
            valid_to = now + timedelta(days=days)
        else:
            valid_to = now + timedelta(hours=24)  # Default 24h
        
        #Step 5: Store forecast in ForecastDb via DAC
        print(f"💾 Storing forecast in ForecastDb...")
        
        model_version = self.model_manager.model_versions.get(
            request.building_id, {}
        ).get(model_used, "1.4.2")
        
        forecast_id = await self.forecast_write.create_forecast(
            forecast_type=request.forecast_type,
            horizon=request.horizon,
            building_id=request.building_id,
            requested_by=request.requested_by,
            series_data=forecast_values,
            valid_from=valid_from,
            valid_to=valid_to,
            model_algorithm=model_used,
            model_version=model_version,
            room_id=request.room_id,
            floor_id=request.floor_id
        )
        
        #Step 6: Return result
        result = ForecastResult(
            forecast_id=forecast_id,
            building_id=request.building_id,
            forecast_type=request.forecast_type,
            horizon=request.horizon,
            values=forecast_values,
            accuracy=accuracy,
            generated_at=now,
            valid_from=valid_from,
            valid_to=valid_to,
            model_used=model_used,
            model_version=model_version
        )
        
        print(f"✅ Forecast {forecast_id} completed successfully")
        print(f"   Model: {model_used} v{model_version}")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   Values: {len(forecast_values)} data points")
        print(f"{'='*60}\n")
        
        return result
    
    async def get_forecast(
        self,
        forecast_id: str,
        requested_by: str
    ) -> Optional[ForecastResult]:
        """
        Retrieve existing forecast by ID.
        """
        forecast_data = await self.forecast_read.get_forecast_by_id(forecast_id)
        
        if not forecast_data:
            return None
        
        return self._convert_to_forecast_result(forecast_data)
    
    async def get_latest_forecast(
        self,
        building_id: str,
        forecast_type: str,
        horizon: str,
        requested_by: str
    ) -> Optional[ForecastResult]:
        """
        Get most recent forecast for a building.
        """
        forecast_data = await self.forecast_read.get_latest_forecast(
            building_id=building_id,
            forecast_type=forecast_type,
            horizon=horizon
        )
        
        if not forecast_data:
            return None
        
        return self._convert_to_forecast_result(forecast_data)
    
    def _convert_to_forecast_result(self, forecast_data) -> ForecastResult:
        """Convert ForecastData to ForecastResult"""
        return ForecastResult(
            forecast_id=forecast_data.id,
            building_id=forecast_data.scope.get('buildingId', ''),
            forecast_type=forecast_data.type,
            horizon=forecast_data.horizon,
            values=forecast_data.series_item,
            accuracy=0.88,  #In production: extract from model_meta
            generated_at=forecast_data.issued_at,
            valid_from=forecast_data.valid_for['from'],
            valid_to=forecast_data.valid_for['to'],
            model_used=forecast_data.model_meta.get('algo', 'LSTM'),
            model_version=forecast_data.model_meta.get('ver', '1.4.2')
        )
    
    # ========================================================================
    # OPTIMIZATION RECOMMENDATIONS
    # ========================================================================
    
    async def get_optimization(
        self,
        request: OptimizationRequest
    ) -> OptimizationResult:
        """
        Generate optimization recommendations.
        
        Implements FR3.
        """
        print(f"\n{'='*60}")
        print(f"💡 OPTIMIZATION REQUEST")
        print(f"{'='*60}")
        print(f"Building: {request.building_id}")
        print(f"Time range: {request.time_range_hours} hours")
        
        #Step 1: Get latest energy forecast (or generate if needed)
        latest_forecast = await self.get_latest_forecast(
            building_id=request.building_id,
            forecast_type="energy_demand",
            horizon="24H",
            requested_by=request.requested_by
        )
        
        if not latest_forecast:
            print("📊 No recent forecast found, generating...")
            forecast_request = ForecastRequest(
                building_id=request.building_id,
                horizon="24H",
                forecast_type="energy_demand",
                requested_by=request.requested_by
            )
            latest_forecast = await self.request_forecast(forecast_request)
        
        #Step 2: Get current consumption baseline
        measurements = await self.measurement.get_measurements(
            building_id=request.building_id,
            metric_type="power_w",
            start_date=datetime.utcnow() - timedelta(hours=24),
            end_date=datetime.utcnow()
        )
        
        current_consumption = sum(m.value for m in measurements) / len(measurements) if measurements else 50000
        
        #Step 3: Generate recommendations
        print("🔍 Analyzing forecast for optimization opportunities...")
        
        recommendations = await self.optimization_engine.generate_recommendations(
            building_id=request.building_id,
            forecast_values=latest_forecast.values,
            current_consumption=current_consumption,
            time_range_hours=request.time_range_hours
        )
        
        #Step 4: Calculate total potential savings
        savings = self.optimization_engine.calculate_savings(recommendations)
        
        result = OptimizationResult(
            building_id=request.building_id,
            recommendations=recommendations,
            total_potential_savings=savings['total_daily'],
            forecast_id=latest_forecast.forecast_id,
            generated_at=datetime.utcnow()
        )
        
        print(f"✅ Generated {len(recommendations)} recommendations")
        print(f"   Total potential savings: {savings['total_daily']:.2f} zł/day")
        print(f"   Monthly projection: {savings['total_monthly']:.2f} zł")
        print(f"{'='*60}\n")
        
        return result
    
    # ========================================================================
    # MODEL MANAGEMENT
    # ========================================================================
    
    async def train_model(
        self,
        building_id: str,
        model_type: str,
        start_date: datetime,
        end_date: datetime,
        requested_by: str
    ) -> Dict[str, Any]:
        """
        Train ML model for a building.
        
        Implements FR5 (retrieve historical data for training).
        """
        print(f"\n{'='*60}")
        print(f"🏋️  MODEL TRAINING REQUEST")
        print(f"{'='*60}")
        print(f"Building: {building_id}")
        print(f"Model: {model_type}")
        print(f"Date range: {start_date} to {end_date}")
        
        days = (end_date - start_date).days
        if days < 30:
            raise ValueError(f"Insufficient training data: {days} days. Need at least 30 days.")
        
        print(f"📥 Retrieving {days} days of historical data...")
        measurements = await self.measurement.get_measurements(
            building_id=building_id,
            metric_type="power_w",
            start_date=start_date,
            end_date=end_date
        )
        
        if len(measurements) < 24 * 30:  # Need at least 30 days of hourly data
            raise InsufficientDataError(
                f"Insufficient measurements: {len(measurements)}. "
                f"Need at least {24 * 30} hourly measurements."
            )
        
        #Train model
        print(f"🔄 Training {model_type} model...")
        result = self.model_manager.train_model(
            building_id=building_id,
            model_type=model_type,
            training_data=measurements
        )
        
        print(f"✅ Model training completed")
        print(f"   Version: {result['model_version']}")
        print(f"   Accuracy: {result['accuracy']:.1%}")
        print(f"{'='*60}\n")
        
        return result
    
    async def get_model_performance(
        self,
        building_id: str,
        model_type: str,
        requested_by: str
    ) -> ModelPerformanceMetrics:
        """
        Get model performance metrics.
        
        Implements FR7 (forecast accuracy metrics).
        """
        performance = self.model_manager.get_model_performance(
            building_id=building_id,
            model_type=model_type
        )
        
        if performance.get('status') == 'not_found':
            raise ModelNotTrainedError(
                f"No {model_type} model found for building {building_id}"
            )
        
        return ModelPerformanceMetrics(
            model_type=model_type,
            model_version=performance['model_version'],
            accuracy=performance['accuracy'],
            mape=performance['mape'],
            rmse=performance['rmse'],
            last_trained=performance['last_trained'],
            training_samples=performance['training_samples'],
            evaluation_date=datetime.utcnow()
        )
    
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    
    async def configure_forecast_parameters(
        self,
        building_id: str,
        parameters: Dict[str, Any],
        requested_by: str
    ) -> bool:
        """
        Configure forecast parameters for a building.
        
        For now: just log the configuration request.
        In production: store in database.
        """
        print(f"⚙️  Configuring forecast parameters for {building_id}:")
        for key, value in parameters.items():
            print(f"   {key}: {value}")
        
        return True
    
    # ========================================================================
    # HEALTH & STATUS
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        uptime = (datetime.utcnow() - self.started_at).total_seconds()
        
        return {
            'status': 'healthy',
            'service': 'ForecastService',
            'version': '1.0.0',
            'uptime_seconds': round(uptime, 1),
            'models_loaded': len(self.model_manager.models),
            'started_at': self.started_at.isoformat()
        }
