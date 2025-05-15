import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import pytest
from trading.data.manager import DataManager

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directories."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    cache_dir = tmp_path / "cache"
    
    raw_dir.mkdir()
    processed_dir.mkdir()
    cache_dir.mkdir()
    
    return {
        "raw": raw_dir,
        "processed": processed_dir,
        "cache": cache_dir
    }

@pytest.fixture
def sample_data():
    """Create sample price data."""
    dates = pd.date_range(start="2024-01-01", end="2024-01-10", freq="D")
    data = {
        "open": [100.0] * len(dates),
        "high": [105.0] * len(dates),
        "low": [95.0] * len(dates),
        "close": [102.0] * len(dates),
        "volume": [1000] * len(dates)
    }
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def data_manager(temp_data_dir, monkeypatch):
    """Create DataManager instance with temporary directories."""
    # Mock config.get to return temporary paths
    def mock_get(key, default=None):
        if key == "data.raw_data_dir":
            return str(temp_data_dir["raw"])
        elif key == "data.processed_data_dir":
            return str(temp_data_dir["processed"])
        elif key == "data.cache_dir":
            return str(temp_data_dir["cache"])
        return default
    
    monkeypatch.setattr("trading.utils.config_manager.config.get", mock_get)
    
    return DataManager()

def test_save_and_load_data(data_manager, sample_data):
    """Test saving and loading data."""
    # Save data
    data_manager.save_data(sample_data, "AAPL", "1d")
    
    # Load data
    loaded_data = data_manager.load_data("AAPL", "1d")
    
    # Check data
    pd.testing.assert_frame_equal(sample_data, loaded_data, check_freq=False)

def test_update_data(data_manager, sample_data):
    """Test updating existing data."""
    # Save initial data
    data_manager.save_data(sample_data, "AAPL", "1d")
    
    # Create new data
    new_dates = pd.date_range(start="2024-01-11", end="2024-01-15", freq="D")
    new_data = pd.DataFrame({
        "open": [110.0] * len(new_dates),
        "high": [115.0] * len(new_dates),
        "low": [105.0] * len(new_dates),
        "close": [112.0] * len(new_dates),
        "volume": [2000] * len(new_dates)
    }, index=new_dates)
    
    # Update data
    data_manager.update_data(new_data, "AAPL", "1d")
    
    # Load updated data
    updated_data = data_manager.load_data("AAPL", "1d")
    
    # Check data
    expected_data = pd.concat([sample_data, new_data])
    pd.testing.assert_frame_equal(expected_data, updated_data, check_freq=False)

def test_cache_data(data_manager, sample_data):
    """Test data caching."""
    # Cache data
    data_manager.cache_data(sample_data, "AAPL", "1d", ttl=1)
    
    # Get cached data
    cached_data = data_manager.get_cached_data("AAPL", "1d")
    
    # Check data
    pd.testing.assert_frame_equal(sample_data, cached_data, check_freq=False)
    
    # Wait for cache to expire
    import time
    time.sleep(1.1)
    
    # Check expired cache
    expired_data = data_manager.get_cached_data("AAPL", "1d")
    assert expired_data is None

def test_get_latest_data(data_manager, sample_data):
    """Test getting latest data timestamp."""
    # Save data
    data_manager.save_data(sample_data, "AAPL", "1d")
    
    # Get latest timestamp
    latest = data_manager.get_latest_data("AAPL", "1d")
    
    # Check timestamp
    assert latest == sample_data.index.max()
    
    # Check non-existent data
    assert data_manager.get_latest_data("NONEXISTENT", "1d") is None

def test_get_data_gaps(data_manager, sample_data):
    """Test finding data gaps."""
    # Save data with gaps
    dates = pd.date_range(start="2024-01-01", end="2024-01-10", freq="D")
    data = sample_data.copy()
    data = data.drop(dates[2:4])  # Create gap
    data_manager.save_data(data, "AAPL", "1d")
    
    # Get gaps
    gaps = data_manager.get_data_gaps(
        "AAPL",
        "1d",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 10)
    )
    
    # Check gaps
    assert len(gaps) == 1
    assert gaps[0][0] == dates[2]
    assert gaps[0][1] == dates[3]
    
    # Check non-existent data
    gaps = data_manager.get_data_gaps(
        "NONEXISTENT",
        "1d",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 10)
    )
    assert len(gaps) == 1
    assert gaps[0][0] == datetime(2024, 1, 1)
    assert gaps[0][1] == datetime(2024, 1, 10)

def test_invalid_data(data_manager):
    """Test handling invalid data."""
    # Empty DataFrame
    with pytest.raises(ValueError):
        data_manager.save_data(pd.DataFrame(), "AAPL", "1d")
    
    # Missing columns
    invalid_data = pd.DataFrame({"open": [100.0]})
    with pytest.raises(ValueError):
        data_manager.save_data(invalid_data, "AAPL", "1d")
    
    # Non-datetime index
    invalid_data = pd.DataFrame({
        "open": [100.0],
        "high": [105.0],
        "low": [95.0],
        "close": [102.0],
        "volume": [1000]
    }, index=[0])
    with pytest.raises(ValueError):
        data_manager.save_data(invalid_data, "AAPL", "1d")

def test_invalid_interval(data_manager, sample_data):
    """Test handling invalid intervals."""
    with pytest.raises(ValueError):
        data_manager.get_data_gaps(
            "AAPL",
            "invalid",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10)
        ) 