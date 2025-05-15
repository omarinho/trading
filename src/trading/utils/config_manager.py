import os
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
import yaml
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from loguru import logger
import json

# Load environment variables
load_dotenv()

class APIConfig(BaseModel):
    """API configuration with validation."""
    timeout: int = Field(default=10, ge=1, le=60)
    retries: int = Field(default=3, ge=1, le=10)
    rate_limit: int = Field(default=2000, ge=1)
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        return v

class DatabaseConfig(BaseModel):
    """Database configuration with validation."""
    host: str = Field(default="localhost")
    port: int = Field(default=27017, ge=1, le=65535)
    name: str = Field(default="trading")
    collections: Dict[str, str] = Field(
        default_factory=lambda: {
            "raw_data": "raw_data",
            "processed_data": "processed_data",
            "backtest_results": "backtest_results",
            "model_metrics": "model_metrics"
        }
    )

class StrategyConfig(BaseModel):
    """Strategy configuration with validation."""
    moving_averages: Dict[str, int] = Field(
        default_factory=lambda: {
            "short_window": 20,
            "long_window": 50
        }
    )
    rsi: Dict[str, int] = Field(
        default_factory=lambda: {
            "period": 14,
            "overbought": 70,
            "oversold": 30
        }
    )
    macd: Dict[str, int] = Field(
        default_factory=lambda: {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        }
    )

    @field_validator('moving_averages')
    @classmethod
    def validate_moving_averages(cls, v: Dict[str, int]) -> Dict[str, int]:
        if v['short_window'] >= v['long_window']:
            raise ValueError("Short window must be less than long window")
        return v

class MLConfig(BaseModel):
    """Machine learning configuration with validation."""
    model_dir: str = Field(default="models/")
    train_test_split: float = Field(default=0.8, gt=0, lt=1)
    validation_split: float = Field(default=0.1, gt=0, lt=1)
    batch_size: int = Field(default=32, ge=1)
    epochs: int = Field(default=100, ge=1)
    early_stopping_patience: int = Field(default=10, ge=1)

    @field_validator('train_test_split', 'validation_split')
    @classmethod
    def validate_splits(cls, v: float, info) -> float:
        if info.field_name == 'validation_split':
            train_test = info.data.get('train_test_split', 0.8)
            if train_test + v >= 1:
                raise ValueError("Sum of splits must be less than 1")
        return v

class ConfigManager:
    """Configuration manager for the trading system.
    
    This class handles loading and accessing configuration data
    from JSON files.
    """
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid
        """
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def get_data_collector_config(self) -> Dict[str, Any]:
        """Get data collector configuration.
        
        Returns:
            Dictionary containing data collector configuration
            
        Raises:
            KeyError: If data collector config is missing
        """
        try:
            return self.config['data_collector']
        except KeyError:
            logger.error("Data collector configuration not found")
            raise KeyError("Data collector configuration not found in config file")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the entire configuration.
        
        Returns:
            Dictionary containing all configuration data
        """
        return self.config

# Create global config instance
config = ConfigManager()

# Example usage:
# from trading.utils.config_manager import config
# 
# # Get validated API config
# api_config = config.get_api_config()
# timeout = api_config.timeout
# 
# # Get database config
# db_config = config.get_database_config()
# host = db_config.host
# 
# # Get path and ensure it exists
# data_dir = config.get_path('data.raw_data_dir')
# 
# # Get environment variable
# api_key = config.get_env('ALPHA_VANTAGE_API_KEY') 