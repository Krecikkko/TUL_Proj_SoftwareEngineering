"""
Configuration Settings for Forecast & Optimization Module

Uses Pydantic Settings for environment-based configuration.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Environment variables should be prefixed with FORECAST_
    Example: FORECAST_DAC_BASE_URL=http://localhost:8001/api/v1
    """
    
    # DAC Service configuration
    dac_base_url: str = "http://localhost:8001/api/v1"
    
    # Use MockDAC for development/testing (False in production)
    use_mock_dac: bool = False
    
    # Service metadata
    service_name: str = "EMSIB Forecast & Optimization"
    service_version: str = "1.0.0"
    
    # HTTP client settings
    dac_timeout_seconds: float = 30.0
    
    class Config:
        env_file = ".env"
        env_prefix = "FORECAST_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are only loaded once
    and reused across the application.
    """
    return Settings()


# Default settings instance
settings = get_settings()
