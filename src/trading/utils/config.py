import os
import yaml
from typing import Dict, Any, Optional
from loguru import logger

class ConfigManager:
    """Manages configuration settings for the trading system.
    
    This class handles loading and accessing configuration settings from:
    1. Environment variables
    2. YAML configuration files
    3. Default values
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Optional path to config file. If not provided,
                        will look for config.yaml in the config directory.
        """
        self.config_path = config_path or os.path.join("config", "config.yaml")
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Default configuration
        self.config = {
            "api": {
                "alpha_vantage": {
                    "api_key": os.getenv("ALPHA_VANTAGE_API_KEY", ""),
                    "base_url": "https://www.alphavantage.co/query",
                    "rate_limit": {
                        "calls_per_minute": 5,
                        "calls_per_day": 500
                    }
                }
            },
            "data": {
                "raw_data_dir": "data/raw",
                "processed_data_dir": "data/processed",
                "cache_dir": "data/cache"
            },
            "logging": {
                "level": "INFO",
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
                "file": "logs/trading.log"
            }
        }
        
        # Load from config file if it exists
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        self._update_config(file_config)
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    def _update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration with new values.
        
        Args:
            new_config: New configuration values
        """
        def update_dict(d: Dict[str, Any], u: Dict[str, Any]) -> None:
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    update_dict(d[k], v)
                else:
                    d[k] = v
        
        update_dict(self.config, new_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (dot-separated for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key (dot-separated for nested keys)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
            
        Raises:
            KeyError: If key not found
        """
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.set(key, value)

# Create global config instance
config = ConfigManager()

# Example usage:
# from trading.utils.config import config
# data_dir = config.get_path('data.raw_data_dir')
# api_key = config.get_env('ALPHA_VANTAGE_API_KEY') 