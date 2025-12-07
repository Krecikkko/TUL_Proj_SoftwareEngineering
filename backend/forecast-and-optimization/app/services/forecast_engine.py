"""
ForecastEngine - Handles forecast generation logic

From our Class Diagram:
- Attributes: model_manager, data_preprocessor, accuracy_threshold
- Methods: generate_forecast(), validate_results()
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from app.schemas.dac_interfaces import IMeasurement, Measurement


class ForecastEngine:
    """
    Engine for generating energy forecasts using ML models.
    
    Responsibilities:
    - Data preprocessing
    - ML model execution
    - Result validation
    """
    
    def __init__(
        self,
        measurement_interface: IMeasurement,
        model_manager: 'MLModelManager',
        accuracy_threshold: float = 0.85
    ):
        """
        Initialize ForecastEngine.
        
        Args:
            measurement_interface: DAC interface for getting historical data
            model_manager: ML model manager
            accuracy_threshold: Minimum acceptable accuracy (default 85%)
        """
        self.measurement = measurement_interface
        self.model_manager = model_manager
        self.accuracy_threshold = accuracy_threshold
    
    async def generate_forecast(
        self,
        building_id: str,
        horizon: str,  # "24H" or "7D"
        forecast_type: str = "energy_demand",
        model_type: str = "auto"
    ) -> Tuple[List[Dict[str, Any]], float, str]:
        """
        Generate forecast for a building.
        
        Process:
        1. Determine forecast parameters (hours to predict)
        2. Retrieve historical data (30+ days)
        3. Preprocess data
        4. Select and load ML model
        5. Generate predictions
        6. Validate results
        
        Args:
            building_id: Building identifier
            horizon: "24H" (24 hours ahead) or "7D" (7 days ahead)
            forecast_type: "energy_demand", "price", or "temp_setpoint"
            model_type: "LSTM", "XGBoost", or "auto"
            
        Returns:
            Tuple of:
            - forecast_values: List of {timestamp, value, confidence}
            - accuracy: Model accuracy (0.0 to 1.0)
            - model_used: "LSTM" or "XGBoost"
            
        Raises:
            InsufficientDataError: If < 30 days of historical data
            ModelNotTrainedError: If model not trained for building
        """
        from app.schemas.forecast_service import InsufficientDataError
        
        #Step 1: Parse horizon to determine prediction length
        hours_ahead = self._parse_horizon(horizon)
        
        #Step 2: Retrieve historical data (need 30+ days)
        training_days = 30
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=training_days)
        
        print(f"📊 Retrieving {training_days} days of data for {building_id}...")
        measurements = await self.measurement.get_measurements(
            building_id=building_id,
            metric_type="power_w",  
            start_date=start_date,
            end_date=end_date
        )
        
        if len(measurements) < 24 * 7:  #Need at least 1 week of hourly data
            raise InsufficientDataError(
                f"Insufficient data: {len(measurements)} measurements. "
                f"Need at least 168 (7 days * 24 hours)"
            )
        
        #Step 3: Preprocess data
        print(f"🔧 Preprocessing {len(measurements)} measurements...")
        processed_data = self._preprocess_data(measurements)
        
        #Step 4: Select model
        if model_type == "auto":
            #Use LSTM for longer horizons, XGBoost for shorter
            model_type = "LSTM" if hours_ahead > 24 else "XGBoost"
        
        print(f"🤖 Using {model_type} model for {hours_ahead}h forecast...")
        
        #Step 5: Generate predictions
        if model_type == "LSTM":
            forecast_values, accuracy = await self._forecast_with_lstm(
                processed_data, hours_ahead
            )
        else:  #XGBoost
            forecast_values, accuracy = await self._forecast_with_xgboost(
                processed_data, hours_ahead
            )
        
        #Step 6: Validate results
        is_valid = self.validate_results(forecast_values, accuracy)
        if not is_valid:
            print(f"⚠️  Warning: Accuracy {accuracy:.1%} below threshold {self.accuracy_threshold:.1%}")
        
        print(f"✅ Forecast generated: {len(forecast_values)} values, accuracy {accuracy:.1%}")
        
        return forecast_values, accuracy, model_type
    
    def _parse_horizon(self, horizon: str) -> int:
        """
        Parse horizon string to hours.
        
        Args:
            horizon: "1H", "8H", "24H", "7D", etc.
            
        Returns:
            Number of hours ahead
        """
        horizon = horizon.upper()
        if horizon.endswith("H"):
            return int(horizon[:-1])
        elif horizon.endswith("D"):
            days = int(horizon[:-1])
            return days * 24
        else:
            return 24
    
    def _preprocess_data(
        self,
        measurements: List[Measurement]
    ) -> pd.DataFrame:
        """
        Preprocess measurement data for ML models.
        
        Steps:
        - Convert to pandas DataFrame
        - Handle missing values (interpolation)
        - Feature engineering (hour, day_of_week, etc.)
        - Normalization
        
        Args:
            measurements: List of Measurement objects
            
        Returns:
            Preprocessed DataFrame
        """
        data = pd.DataFrame([
            {
                'timestamp': m.timestamp,
                'value': m.value
            }
            for m in measurements
        ])
        
        data = data.sort_values('timestamp').reset_index(drop=True)
        
        data.set_index('timestamp', inplace=True)
        data = data.resample('1h').mean()  
        
        data['value'] = data['value'].interpolate(method='time')
        
        data['hour'] = data.index.hour
        data['day_of_week'] = data.index.dayofweek
        data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
        
        #Add rolling statistics (for XGBoost)
        data['rolling_mean_24h'] = data['value'].rolling(window=24, min_periods=1).mean()
        data['rolling_std_24h'] = data['value'].rolling(window=24, min_periods=1).std()
        
        return data
    
    async def _forecast_with_lstm(
        self,
        data: pd.DataFrame,
        hours_ahead: int
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Generate forecast using LSTM model.
        
        MOCK IMPLEMENTATION: Returns realistic-looking predictions.
        In production, this would use actual TensorFlow/PyTorch LSTM.
        
        Args:
            data: Preprocessed DataFrame
            hours_ahead: Hours to forecast
            
        Returns:
            Tuple of (forecast_values, accuracy)
        """
        #MOCK: Generate predictions based on patterns in historical data
        last_24h = data['value'].tail(24).values
        mean_value = np.mean(last_24h)
        std_value = np.std(last_24h)
        
        forecast_values = []
        current_time = data.index[-1] + timedelta(hours=1)
        
        for i in range(hours_ahead):
            #Simulate daily pattern (higher during day, lower at night)
            hour = current_time.hour
            time_factor = 1.2 if 8 <= hour <= 18 else 0.8
            
            #Add weekly pattern (lower on weekends)
            day_factor = 0.85 if current_time.weekday() in [5, 6] else 1.0
            
            #Predict with some noise
            predicted_value = mean_value * time_factor * day_factor
            predicted_value += np.random.normal(0, std_value * 0.1)
            
            #Confidence decreases over time
            confidence = 0.95 - (i / hours_ahead) * 0.15
            
            forecast_values.append({
                'timestamp': current_time.isoformat(),
                'value': max(0, predicted_value),  # Ensure non-negative
                'confidence': round(confidence, 3)
            })
            
            current_time += timedelta(hours=1)
        
        #MOCK accuracy: LSTM typically 85-92% for 24h forecasts
        accuracy = 0.88 - (hours_ahead / 1000)  # Slightly lower for longer horizons
        
        return forecast_values, accuracy
    
    async def _forecast_with_xgboost(
        self,
        data: pd.DataFrame,
        hours_ahead: int
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Generate forecast using XGBoost model.
        
        MOCK IMPLEMENTATION: Returns realistic-looking predictions.
        In production, this would use actual scikit-learn XGBoost.
        
        Args:
            data: Preprocessed DataFrame  
            hours_ahead: Hours to forecast
            
        Returns:
            Tuple of (forecast_values, accuracy)
        """
        #MOCK: Generate predictions based on features
        forecast_values = []
        current_time = data.index[-1] + timedelta(hours=1)
        
        for i in range(hours_ahead):
            hour = current_time.hour
            day_of_week = current_time.weekday()
            is_weekend = 1 if day_of_week in [5, 6] else 0
            
            #Use rolling mean as base prediction
            rolling_mean = data['rolling_mean_24h'].iloc[-1]
            
            #Adjust based on features
            hour_factor = 1.3 if 8 <= hour <= 18 else 0.7
            weekend_factor = 0.8 if is_weekend else 1.0
            
            predicted_value = rolling_mean * hour_factor * weekend_factor
            predicted_value += np.random.normal(0, rolling_mean * 0.05)
            
            #XGBoost confidence typically lower than LSTM
            confidence = 0.90 - (i / hours_ahead) * 0.20
            
            forecast_values.append({
                'timestamp': current_time.isoformat(),
                'value': max(0, predicted_value),
                'confidence': round(confidence, 3)
            })
            
            current_time += timedelta(hours=1)
        
        #MOCK accuracy: XGBoost typically 82-88% for 24h forecasts
        accuracy = 0.85 - (hours_ahead / 1200)
        
        return forecast_values, accuracy
    
    def validate_results(
        self,
        forecast_values: List[Dict[str, Any]],
        accuracy: float
    ) -> bool:
        """
        Validate forecast results against quality thresholds.
        
        Validation checks:
        - Accuracy meets threshold (≥85%)
        - Values are non-negative
        - Values are within physical limits
        - No extreme outliers
        
        Args:
            forecast_values: List of predictions
            accuracy: Model accuracy
            
        Returns:
            True if valid, False otherwise
        """
        #Check accuracy threshold
        if accuracy < self.accuracy_threshold:
            print(f"⚠️  Accuracy {accuracy:.1%} below threshold {self.accuracy_threshold:.1%}")
            return False
        
        #Check all values are non-negative
        values = [f['value'] for f in forecast_values]
        if any(v < 0 for v in values):
            print("⚠️  Negative values detected")
            return False
        
        #Check for extreme outliers (> 5x mean)
        mean_value = np.mean(values)
        if any(v > mean_value * 5 for v in values):
            print("⚠️  Extreme outliers detected")
            return False
        
        return True
