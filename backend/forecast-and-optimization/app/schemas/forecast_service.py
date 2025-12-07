"""
IForecastService Interface

This is the interface WE PROVIDE to other teams.
The Alerts, Authorization & Communication team should use this to access our module.

Team: Daniyar Zhumatayev & Kuzma Martysiuk
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ForecastRequest(BaseModel):
    """
    Request for generating an energy forecast.
    From our Class Diagram.
    """
    building_id: str
    horizon: str  # "24H" or "7D"
    forecast_type: str = "energy_demand"  # "energy_demand", "price", "temp_setpoint"
    requested_by: str  # User ID
    room_id: Optional[str] = None  # Optional: forecast for specific room
    floor_id: Optional[str] = None  # Optional: forecast for specific floor


class ForecastResult(BaseModel):
    """
    Result of a forecast generation.
    From our Class Diagram.
    """
    forecast_id: str
    building_id: str
    forecast_type: str
    horizon: str
    values: List[Dict[str, Any]]  # [{timestamp, value, confidence}, ...]
    accuracy: float  # Model accuracy metric (e.g., 0.88 = 88%)
    generated_at: datetime
    valid_from: datetime
    valid_to: datetime
    model_used: str  # "LSTM" or "XGBoost"
    model_version: str


class OptimizationRequest(BaseModel):
    """
    Request for generating optimization recommendations.
    """
    building_id: str
    requested_by: str
    time_range_hours: int = 24  # How far ahead to optimize (default 24h)


class OptimizationRecommendation(BaseModel):
    """
    A single optimization recommendation.
    From our Class Diagram.
    """
    action_type: str  # "reduce_heating", "shift_load", "use_renewable", etc.
    estimated_savings: float  # Estimated cost savings in PLN (Polish złoty)
    estimated_savings_pct: float  # Percentage savings
    priority: int  # 1-5, where 1 is highest priority
    description: str  # Human-readable description
    time_window: Dict[str, datetime]  # {start, end} when to apply
    parameters: Optional[Dict[str, Any]] = None  # Specific parameters for action


class OptimizationResult(BaseModel):
    """
    Result of optimization recommendation generation.
    """
    building_id: str
    recommendations: List[OptimizationRecommendation]
    total_potential_savings: float  # Total if all recommendations applied
    forecast_id: str  # Which forecast was used for optimization
    generated_at: datetime


class ModelPerformanceMetrics(BaseModel):
    """
    Performance metrics for ML models (for FR7).
    """
    model_type: str  # "LSTM" or "XGBoost"
    model_version: str
    accuracy: float  # Overall accuracy (e.g., 0.85 = 85%)
    mape: float  # Mean Absolute Percentage Error
    rmse: float  # Root Mean Square Error
    last_trained: datetime
    training_samples: int
    evaluation_date: datetime


# ============================================================================
# IFORECASTSERVICE INTERFACE
# ============================================================================

class IForecastService(ABC):
    """
    Main interface provided by Forecast and Optimization module.
    
    This is what other teams (AAC, Frontend) will use to interact with our module.
    
    Fulfills functional requirements:
    - FR1: Generate energy consumption forecasts using ML algorithms
    - FR2: Generate cost forecasts based on predicted consumption and pricing
    - FR3: Provide optimization recommendations for energy usage
    - FR4: Store forecast results in ForecastDb via DAC
    - FR5: Retrieve historical measurement data for model training
    - FR6: Support multiple forecast horizons (24h, 7 days)
    - FR7: Provide forecast accuracy metrics and model performance tracking
    - FR8: Handle forecast requests from authorized users via IForecastService
    """
    
    # ========================================================================
    # FORECAST GENERATION (FR1, FR2, FR6, FR8)
    # ========================================================================
    
    @abstractmethod
    async def request_forecast(
        self,
        request: ForecastRequest
    ) -> ForecastResult:
        """
        Generate an energy consumption or cost forecast.
        
        This is our main endpoint that other teams will call.
        
        Process:
        1. Validate request parameters
        2. Check if user is authorized (via building access)
        3. Retrieve historical data via DAC (IMeasurement)
        4. Preprocess data
        5. Load appropriate ML model (LSTM or XGBoost)
        6. Generate forecast
        7. Validate results (accuracy threshold)
        8. Store forecast via DAC (IForecastWrite)
        9. Return ForecastResult
        
        Args:
            request: ForecastRequest with building_id, horizon, etc.
            
        Returns:
            ForecastResult with forecast_id, values, accuracy, etc.
            
        Raises:
            ValueError: If request validation fails or insufficient data
            PermissionError: If user lacks access to building
            RuntimeError: If forecast generation fails
            
        Performance requirement: Must complete within 30 seconds (NFR)
        Accuracy requirement: Must achieve ≥85% accuracy for 24h (NFR)
        """
        pass
    
    @abstractmethod
    async def get_forecast(
        self,
        forecast_id: str,
        requested_by: str
    ) -> Optional[ForecastResult]:
        """
        Retrieve an existing forecast by ID.
        
        Args:
            forecast_id: Forecast identifier
            requested_by: User ID requesting forecast
            
        Returns:
            ForecastResult or None if not found
            
        Raises:
            PermissionError: If user lacks access to forecast
        """
        pass
    
    @abstractmethod
    async def get_latest_forecast(
        self,
        building_id: str,
        forecast_type: str,
        horizon: str,
        requested_by: str
    ) -> Optional[ForecastResult]:
        """
        Get the most recent forecast for a building.
        
        Useful for optimization engine and UI to avoid regenerating.
        
        Args:
            building_id: Building identifier
            forecast_type: "energy_demand", "price", or "temp_setpoint"
            horizon: "24H" or "7D"
            requested_by: User ID
            
        Returns:
            Most recent ForecastResult or None
        """
        pass
    
    # ========================================================================
    # OPTIMIZATION RECOMMENDATIONS (FR3)
    # ========================================================================
    
    @abstractmethod
    async def get_optimization(
        self,
        request: OptimizationRequest
    ) -> OptimizationResult:
        """
        Generate cost optimization recommendations.
        
        This uses forecasts to identify opportunities to reduce costs:
        - Shift loads to off-peak hours
        - Reduce heating/cooling during low occupancy
        - Use renewable energy when available
        - Adjust temperature setpoints
        
        Process:
        1. Get latest energy forecast (or generate if needed)
        2. Retrieve current pricing data
        3. Retrieve current consumption patterns
        4. Analyze for optimization opportunities
        5. Generate prioritized recommendations
        6. Calculate estimated savings
        7. Store recommendations
        8. Return OptimizationResult
        
        Args:
            request: OptimizationRequest with building_id, time_range
            
        Returns:
            OptimizationResult with list of recommendations
            
        Raises:
            ValueError: If no forecast available
            PermissionError: If user lacks access
        """
        pass
    
    # ========================================================================
    # MODEL MANAGEMENT & PERFORMANCE (FR5, FR7)
    # ========================================================================
    
    @abstractmethod
    async def train_model(
        self,
        building_id: str,
        model_type: str,  # "LSTM" or "XGBoost"
        start_date: datetime,
        end_date: datetime,
        requested_by: str
    ) -> Dict[str, Any]:
        """
        Train or retrain ML model for a building.
        
        This is typically run:
        - Monthly (scheduled retraining)
        - When accuracy drops below threshold
        - After significant building changes
        
        Args:
            building_id: Building to train model for
            model_type: "LSTM" or "XGBoost"
            start_date: Start of training data range
            end_date: End of training data range
            requested_by: User ID (admin only)
            
        Returns:
            Dict with training results:
            {
                "model_version": "1.4.2",
                "accuracy": 0.88,
                "training_samples": 720,
                "training_duration_seconds": 45.2,
                "status": "success"
            }
            
        Raises:
            ValueError: If insufficient data (need 30+ days)
            PermissionError: If user not admin
        """
        pass
    
    @abstractmethod
    async def get_model_performance(
        self,
        building_id: str,
        model_type: str,
        requested_by: str
    ) -> ModelPerformanceMetrics:
        """
        Get performance metrics for current model (FR7).
        
        Used for monitoring and triggering retraining.
        
        Args:
            building_id: Building identifier
            model_type: "LSTM" or "XGBoost"
            requested_by: User ID
            
        Returns:
            ModelPerformanceMetrics with accuracy, MAPE, RMSE, etc.
        """
        pass
    
    # ========================================================================
    # CONFIGURATION (FR6)
    # ========================================================================
    
    @abstractmethod
    async def configure_forecast_parameters(
        self,
        building_id: str,
        parameters: Dict[str, Any],
        requested_by: str
    ) -> bool:
        """
        Configure forecast parameters for a building.
        
        Configurable parameters:
        - Default horizon ("24H" or "7D")
        - Accuracy threshold (default 0.85)
        - Model preference ("LSTM", "XGBoost", or "auto")
        - Retraining schedule
        
        Args:
            building_id: Building identifier
            parameters: Dict of parameters to configure
            requested_by: User ID (admin only)
            
        Returns:
            True if successful
            
        Raises:
            PermissionError: If user not admin
        """
        pass
    
    # ========================================================================
    # HEALTH & STATUS
    # ========================================================================
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health status of Forecast & Optimization module.
        
        Returns:
            Dict with status information:
            {
                "status": "healthy",
                "models_loaded": True,
                "dac_connection": True,
                "last_forecast": "2025-12-06T14:30:00Z",
                "uptime_seconds": 86400
            }
        """
        pass


# ============================================================================
# ERRORS
# ============================================================================

class ForecastError(Exception):
    """Base exception for forecast-related errors"""
    pass


class InsufficientDataError(ForecastError):
    """Raised when insufficient historical data for forecasting"""
    pass


class ModelNotTrainedError(ForecastError):
    """Raised when ML model not yet trained for building"""
    pass


class AccuracyBelowThresholdError(ForecastError):
    """Raised when forecast accuracy below acceptable threshold"""
    pass
