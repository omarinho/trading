import os
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
import yaml
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from loguru import logger

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
    """Configuration management for the trading system.
    
    This class:
    - Loads and validates YAML configuration
    - Manages environment variables
    - Provides type-safe access to config values
    - Handles default values and validation
    - Ensures all paths exist
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.root_dir = Path(__file__).parent.parent.parent.parent
        self.config_path = config_path or str(self.root_dir / "config" / "config.yaml")
        self._config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """Load and validate configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                raw_config = yaml.safe_load(f)
                
            # Validate and convert to Pydantic models
            self._config = {
                "api": APIConfig(**raw_config.get("api", {})),
                "database": DatabaseConfig(**raw_config.get("database", {})),
                "strategy": StrategyConfig(**raw_config.get("strategy", {})),
                "ml": MLConfig(**raw_config.get("ml", {})),
                "data": raw_config.get("data", {}),
                "backtest": raw_config.get("backtest", {}),
                "logging": raw_config.get("logging", {}),
                "visualization": raw_config.get("visualization", {})
            }
            
        except FileNotFoundError:
            logger.warning(f"Config file not found at {self.config_path}, using defaults")
            self._config = self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return validated default configuration."""
        return {
            "api": APIConfig(),
            "database": DatabaseConfig(),
            "strategy": StrategyConfig(),
            "ml": MLConfig(),
            "data": {
                "raw_data_dir": str(self.root_dir / "data" / "raw"),
                "processed_data_dir": str(self.root_dir / "data" / "processed"),
                "cache_dir": str(self.root_dir / "data" / "cache"),
            },
            "backtest": {
                "initial_capital": 100000.0,
                "commission": 0.001,
                "slippage": 0.0005,
            },
            "logging": {
                "level": "INFO",
                "file": str(self.root_dir / "logs" / "trading.log"),
            },
            "visualization": {
                "style": "seaborn",
                "context": "paper",
                "palette": "deep",
                "dpi": 300,
                "save_dir": str(self.root_dir / "plots"),
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'data.raw_data_dir')."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            elif hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        return value
    
    def get_env(self, key: str, default: Any = None) -> str:
        """Get environment variable with validation."""
        value = os.getenv(key, default)
        if value is None:
            logger.warning(f"Environment variable {key} not found")
        return value
    
    def get_path(self, key: str) -> Path:
        """Get path from config and ensure directory exists."""
        path = Path(self.get(key))
        if not path.is_absolute():
            path = self.root_dir / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_api_config(self) -> APIConfig:
        """Get validated API configuration."""
        return self._config["api"]
    
    def get_database_config(self) -> DatabaseConfig:
        """Get validated database configuration."""
        return self._config["database"]
    
    def get_strategy_config(self) -> StrategyConfig:
        """Get validated strategy configuration."""
        return self._config["strategy"]
    
    def get_ml_config(self) -> MLConfig:
        """Get validated machine learning configuration."""
        return self._config["ml"]
    
    def validate(self) -> bool:
        """Validate entire configuration."""
        try:
            # Validate all Pydantic models
            for key, value in self._config.items():
                if isinstance(value, BaseModel):
                    value.model_validate(value.model_dump())
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

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