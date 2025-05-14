import pytest
from pathlib import Path
import yaml
from trading.utils.config_manager import (
    ConfigManager,
    APIConfig,
    DatabaseConfig,
    StrategyConfig,
    MLConfig
)

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file for testing."""
    config = {
        "api": {
            "timeout": 5,
            "retries": 2,
            "rate_limit": 1000
        },
        "database": {
            "host": "test_host",
            "port": 27018,
            "name": "test_db",
            "collections": {
                "raw_data": "test_raw",
                "processed_data": "test_processed"
            }
        },
        "strategy": {
            "moving_averages": {
                "short_window": 10,
                "long_window": 30
            },
            "rsi": {
                "period": 14,
                "overbought": 70,
                "oversold": 30
            }
        },
        "ml": {
            "model_dir": "test_models/",
            "train_test_split": 0.7,
            "validation_split": 0.15,
            "batch_size": 64,
            "epochs": 50
        }
    }
    
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    return config_path

def test_config_loading(temp_config_file):
    """Test that config loads correctly from file."""
    config = ConfigManager(str(temp_config_file))
    
    # Test API config
    api_config = config.get_api_config()
    assert api_config.timeout == 5
    assert api_config.retries == 2
    assert api_config.rate_limit == 1000
    
    # Test database config
    db_config = config.get_database_config()
    assert db_config.host == "test_host"
    assert db_config.port == 27018
    assert db_config.name == "test_db"
    
    # Test strategy config
    strategy_config = config.get_strategy_config()
    assert strategy_config.moving_averages["short_window"] == 10
    assert strategy_config.moving_averages["long_window"] == 30
    
    # Test ML config
    ml_config = config.get_ml_config()
    assert ml_config.train_test_split == 0.7
    assert ml_config.validation_split == 0.15
    assert ml_config.batch_size == 64

def test_default_config():
    """Test that default config is loaded when no file exists."""
    config = ConfigManager("nonexistent.yaml")
    
    # Test default API config
    api_config = config.get_api_config()
    assert api_config.timeout == 10
    assert api_config.retries == 3
    
    # Test default database config
    db_config = config.get_database_config()
    assert db_config.host == "localhost"
    assert db_config.port == 27017

def test_config_validation():
    """Test that config validation works correctly."""
    # Test invalid API config
    with pytest.raises(ValueError):
        APIConfig(timeout=0)
    
    # Test invalid strategy config
    with pytest.raises(ValueError):
        StrategyConfig(moving_averages={"short_window": 50, "long_window": 20})
    
    # Test invalid ML config
    with pytest.raises(ValueError):
        MLConfig(train_test_split=0.9, validation_split=0.2)

def test_path_creation():
    """Test that paths are created correctly."""
    config = ConfigManager()
    
    # Test data directory creation
    data_dir = config.get_path('data.raw_data_dir')
    assert data_dir.exists()
    assert data_dir.is_dir()
    
    # Test log directory creation
    log_dir = config.get_path('logging.file').parent
    assert log_dir.exists()
    assert log_dir.is_dir()

def test_env_variables(monkeypatch):
    """Test environment variable handling."""
    config = ConfigManager()
    
    # Test existing env var
    monkeypatch.setenv("TEST_VAR", "test_value")
    assert config.get_env("TEST_VAR") == "test_value"
    
    # Test missing env var
    assert config.get_env("NONEXISTENT_VAR", "default") == "default"

def test_dot_notation():
    """Test dot notation access to config values."""
    config = ConfigManager()
    
    # Test nested access
    assert isinstance(config.get('api.timeout'), int)
    assert isinstance(config.get('database.host'), str)
    
    # Test default value
    assert config.get('nonexistent.key', 'default') == 'default' 