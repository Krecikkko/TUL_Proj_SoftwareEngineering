"""
OptimizationEngine - Generates cost optimization recommendations

From our Class Diagram:
- Attributes: cost_calculator, constraints, pricing_data
- Methods: generate_recommendations(), calculate_savings()
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.schemas.forecast_service import OptimizationRecommendation


class OptimizationEngine:
    """
    Engine for generating energy cost optimization recommendations.
    
    Responsibilities:
    - Analyze forecasts for optimization opportunities
    - Calculate potential cost savings
    - Generate prioritized recommendations
    """
    
    def __init__(self):
        """Initialize OptimizationEngine with default pricing"""
        #MOCK: Simple time-of-use pricing for Poland (real system would get from pricing API)
        #Based on typical Polish energy prices (2025)
        self.pricing = {
            'peak': 1.05,      #1.05 zł/kWh during peak hours (9-21)
            'off_peak': 0.65,  #0.65 zł/kWh during off-peak hours
            'super_off_peak': 0.45  #0.45 zł/kWh during super off-peak (23-6)
        }
        
        #Optimization constraints (can be configured per building)
        self.constraints = {
            'min_temp_c': 18,      #Minimum temperature (comfort)
            'max_temp_c': 26,      #Maximum temperature
            'max_load_shift_kwh': 100,  #Max load that can be shifted
            'min_savings_threshold': 20.0  #Minimum 20 zł savings to recommend
        }
    
    async def generate_recommendations(
        self,
        building_id: str,
        forecast_values: List[Dict[str, Any]],
        current_consumption: float,
        time_range_hours: int = 24
    ) -> List[OptimizationRecommendation]:
        """
        Generate optimization recommendations based on forecast.
        
        Analyzes the forecast to identify:
        1. Load shifting opportunities (move consumption to off-peak)
        2. Temperature setpoint adjustments
        3. Peak demand reduction strategies
        4. Renewable energy utilization (if available)
        
        Args:
            building_id: Building identifier
            forecast_values: Energy forecast from ForecastEngine
            current_consumption: Current average consumption (kW)
            time_range_hours: Hours to optimize (default 24)
            
        Returns:
            List of OptimizationRecommendation sorted by priority
        """
        recommendations = []
        
        #Analyze forecast for opportunities
        print(f"🔍 Analyzing {len(forecast_values)} forecast values for optimization...")
        
        #1. Load Shifting Opportunities
        load_shift_recs = self._analyze_load_shifting(
            forecast_values[:time_range_hours]
        )
        recommendations.extend(load_shift_recs)
        
        #2. Peak Demand Reduction
        peak_reduction_recs = self._analyze_peak_reduction(
            forecast_values[:time_range_hours]
        )
        recommendations.extend(peak_reduction_recs)
        
        #3. Temperature Setpoint Optimization
        temp_optimization_recs = self._analyze_temperature_optimization(
            forecast_values[:time_range_hours],
            current_consumption
        )
        recommendations.extend(temp_optimization_recs)
        
        #4. Renewable Energy Utilization (if applicable)
        #In mock: skip this if no renewable data
        
        #Sort by priority (1 = highest) and potential savings
        recommendations.sort(key=lambda r: (r.priority, -r.estimated_savings))
        
        print(f"✅ Generated {len(recommendations)} optimization recommendations")
        
        return recommendations
    
    def _analyze_load_shifting(
        self,
        forecast_values: List[Dict[str, Any]]
    ) -> List[OptimizationRecommendation]:
        """
        Identify opportunities to shift load to off-peak hours.
        
        Strategy:
        - Find high consumption during peak hours
        - Check if load can be shifted to off-peak
        - Calculate savings from price differential
        """
        recommendations = []
        
        peak_hours = []
        off_peak_hours = []
        
        for i, forecast in enumerate(forecast_values):
            timestamp = datetime.fromisoformat(forecast['timestamp'])
            hour = timestamp.hour
            value_kw = forecast['value'] / 1000  #Convert W to kW
            
            if 9 <= hour < 21:  #Peak hours
                peak_hours.append((i, timestamp, value_kw))
            elif 23 <= hour or hour < 6:  #Super off-peak
                off_peak_hours.append((i, timestamp, value_kw))
        
        #Find high peak consumption
        if peak_hours:
            peak_hours.sort(key=lambda x: x[2], reverse=True)
            top_peak = peak_hours[0]
            
            if top_peak[2] > 80:  #If > 80 kW during peak
                #Calculate savings if 20% shifted to off-peak
                shift_amount = top_peak[2] * 0.20
                savings = shift_amount * (self.pricing['peak'] - self.pricing['super_off_peak'])
                
                if savings >= self.constraints['min_savings_threshold']:
                    recommendations.append(OptimizationRecommendation(
                        action_type="shift_load",
                        estimated_savings=round(savings, 2),
                        estimated_savings_pct=round((savings / (top_peak[2] * self.pricing['peak'])) * 100, 1),
                        priority=1,
                        description=f"Shift {shift_amount:.1f} kW of non-critical load from {top_peak[1].strftime('%H:%M')} to super off-peak hours (23:00-06:00) to save on peak pricing",
                        time_window={
                            'start': top_peak[1],
                            'end': top_peak[1] + timedelta(hours=1)
                        },
                        parameters={
                            'load_to_shift_kw': round(shift_amount, 1),
                            'suggested_target_hour': 23
                        }
                    ))
        
        return recommendations
    
    def _analyze_peak_reduction(
        self,
        forecast_values: List[Dict[str, Any]]
    ) -> List[OptimizationRecommendation]:
        """
        Identify peak demand reduction opportunities.
        
        Peak demand charges can be significant, so reducing maximum demand
        is valuable even if total consumption stays same.
        """
        recommendations = []
        
        max_demand = max(f['value'] for f in forecast_values) / 1000  
        avg_demand = np.mean([f['value'] for f in forecast_values]) / 1000
        
        #If peak is >30% above average, recommend reduction
        if max_demand > avg_demand * 1.3:
            #Find when peak occurs
            peak_forecast = max(forecast_values, key=lambda f: f['value'])
            peak_time = datetime.fromisoformat(peak_forecast['timestamp'])
            
            #Calculate savings (peak demand charges ~60 zł/kW/month in Poland)
            reduction_target = (max_demand - avg_demand * 1.2) * 0.5
            monthly_savings = reduction_target * 60  
            daily_savings = monthly_savings / 30
            
            if daily_savings >= self.constraints['min_savings_threshold']:
                recommendations.append(OptimizationRecommendation(
                    action_type="reduce_peak_demand",
                    estimated_savings=round(daily_savings, 2),
                    estimated_savings_pct=round((reduction_target / max_demand) * 100, 1),
                    priority=2,
                    description=f"Reduce peak demand by {reduction_target:.1f} kW at {peak_time.strftime('%H:%M')} through temporary load curtailment or equipment sequencing",
                    time_window={
                        'start': peak_time - timedelta(minutes=30),
                        'end': peak_time + timedelta(minutes=30)
                    },
                    parameters={
                        'target_reduction_kw': round(reduction_target, 1),
                        'current_peak_kw': round(max_demand, 1)
                    }
                ))
        
        return recommendations
    
    def _analyze_temperature_optimization(
        self,
        forecast_values: List[Dict[str, Any]],
        current_consumption: float
    ) -> List[OptimizationRecommendation]:
        """
        Optimize HVAC temperature setpoints for energy savings.
        
        Strategy:
        - During low occupancy periods, allow wider temperature range
        - Precool/preheat during off-peak pricing
        """
        recommendations = []
        
        #Identify low-occupancy periods (nights, weekends)
        for i, forecast in enumerate(forecast_values):
            timestamp = datetime.fromisoformat(forecast['timestamp'])
            hour = timestamp.hour
            is_weekend = timestamp.weekday() in [5, 6]
            
            if (22 <= hour or hour < 6) or is_weekend:
                hvac_portion = current_consumption * 0.45
                
                #Relaxing setpoint by 2°C can save ~10% HVAC energy
                savings = hvac_portion * 0.10 * self.pricing['super_off_peak']
                
                if savings >= self.constraints['min_savings_threshold']:
                    recommendations.append(OptimizationRecommendation(
                        action_type="adjust_temperature",
                        estimated_savings=round(savings, 2),
                        estimated_savings_pct=10.0,
                        priority=3,
                        description=f"During low occupancy at {timestamp.strftime('%H:%M')}, adjust temperature setpoint by ±2°C (heating: 20°C→18°C, cooling: 24°C→26°C) to reduce HVAC load",
                        time_window={
                            'start': timestamp,
                            'end': timestamp + timedelta(hours=1)
                        },
                        parameters={
                            'heating_setpoint_c': 18,
                            'cooling_setpoint_c': 26,
                            'current_heating_setpoint_c': 20,
                            'current_cooling_setpoint_c': 24
                        }
                    ))
                    break  
        
        return recommendations
    
    def calculate_savings(
        self,
        recommendations: List[OptimizationRecommendation]
    ) -> Dict[str, float]:
        """
        Calculate total potential savings from recommendations.
        
        Args:
            recommendations: List of optimization recommendations
            
        Returns:
            Dict with:
            - total_daily: Total daily savings if all applied
            - total_monthly: Projected monthly savings
            - total_annual: Projected annual savings
            - by_priority: Breakdown by priority level
        """
        if not recommendations:
            return {
                'total_daily': 0.0,
                'total_monthly': 0.0,
                'total_annual': 0.0,
                'by_priority': {}
            }
        
        total_daily = sum(r.estimated_savings for r in recommendations)
        
        by_priority = {}
        for priority in [1, 2, 3, 4, 5]:
            priority_recs = [r for r in recommendations if r.priority == priority]
            by_priority[priority] = sum(r.estimated_savings for r in priority_recs)
        
        return {
            'total_daily': round(total_daily, 2),
            'total_monthly': round(total_daily * 30, 2),
            'total_annual': round(total_daily * 365, 2),
            'by_priority': by_priority
        }
