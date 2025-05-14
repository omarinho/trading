import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration management for the trading system.
    
    This class handles:
    - Environment variables (API keys, secrets)
    - YAML configuration files
    - Default settings
    - Path management
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.root_dir = Path(__file__).parent.parent.parent
        self.config_path = config_path or str(self.root_dir / "config" / "config.yaml")
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {self.config_path}, using defaults")
            self.config = self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
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
            "api": {
                "yfinance": {
                    "timeout": 10,
                    "retries": 3,
                },
            },
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'data.raw_data_dir')."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def get_env(self, key: str, default: Any = None) -> str:
        """Get environment variable."""
        return os.getenv(key, default)
    
    def get_path(self, key: str) -> Path:
        """Get path from config and ensure directory exists."""
        path = Path(self.get(key))
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

# Create global config instance
config = Config()

# Example usage:
# from trading.utils.config import config
# data_dir = config.get_path('data.raw_data_dir')
# api_key = config.get_env('ALPHA_VANTAGE_API_KEY') 