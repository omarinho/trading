#!/usr/bin/env python
import os
import shutil
from pathlib import Path
import yaml
from loguru import logger

def create_directory_structure():
    """Create the project directory structure."""
    directories = [
        "data/raw",
        "data/processed",
        "data/cache",
        "logs",
        "models",
        "plots",
        "notebooks",
        "config",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def create_env_file():
    """Create .env file with default values."""
    env_content = """
# API Keys (DO NOT COMMIT ACTUAL KEYS)
ALPHA_VANTAGE_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here

# Database Configuration
DB_HOST=localhost
DB_PORT=27017
DB_NAME=trading
DB_USER=your_user
DB_PASSWORD=your_password

# Trading Configuration
INITIAL_CAPITAL=100000
MAX_POSITION_SIZE=0.1  # 10% of portfolio
RISK_PER_TRADE=0.02    # 2% risk per trade

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trading.log

# Data Directories
RAW_DATA_DIR=data/raw
PROCESSED_DATA_DIR=data/processed
CACHE_DIR=data/cache

# Backtesting
BACKTEST_START_DATE=2020-01-01
BACKTEST_END_DATE=2023-12-31
COMMISSION_RATE=0.001
SLIPPAGE=0.0005
"""
    
    with open(".env", "w") as f:
        f.write(env_content.strip())
    logger.info("Created .env file")

def create_config_file():
    """Create config.yaml file with default values."""
    config_content = """
# Trading System Configuration

# Data Management
data:
  raw_data_dir: data/raw
  processed_data_dir: data/processed
  cache_dir: data/cache
  symbols:
    - AAPL
    - MSFT
    - GOOGL
    - AMZN
    - META
  timeframes:
    - 1m
    - 5m
    - 15m
    - 1h
    - 1d

# Backtesting Configuration
backtest:
  initial_capital: 100000.0
  commission: 0.001
  slippage: 0.0005
  start_date: "2020-01-01"
  end_date: "2023-12-31"
  risk_per_trade: 0.02
  max_position_size: 0.1

# Strategy Parameters
strategy:
  moving_averages:
    short_window: 20
    long_window: 50
  rsi:
    period: 14
    overbought: 70
    oversold: 30
  macd:
    fast_period: 12
    slow_period: 26
    signal_period: 9

# Machine Learning
ml:
  model_dir: models/
  train_test_split: 0.8
  validation_split: 0.1
  batch_size: 32
  epochs: 100
  early_stopping_patience: 10

# API Configuration
api:
  yfinance:
    timeout: 10
    retries: 3
    rate_limit: 2000  # requests per hour
  polygon:
    timeout: 10
    retries: 3
    rate_limit: 5000  # requests per minute

# Logging
logging:
  level: INFO
  file: logs/trading.log
  max_size: 500MB
  backup_count: 10

# Database
database:
  host: localhost
  port: 27017
  name: trading
  collections:
    raw_data: raw_data
    processed_data: processed_data
    backtest_results: backtest_results
    model_metrics: model_metrics

# Visualization
visualization:
  style: seaborn
  context: paper
  palette: deep
  dpi: 300
  save_dir: plots/
"""
    
    config_path = Path("config/config.yaml")
    with open(config_path, "w") as f:
        f.write(config_content.strip())
    logger.info(f"Created {config_path}")

def create_gitignore():
    """Create .gitignore file if it doesn't exist."""
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Jupyter Notebook
.ipynb_checkpoints
notebooks/.ipynb_checkpoints/

# Data
data/raw/
data/processed/
data/cache/

# Logs
logs/
*.log

# Environment variables
.env

# Model files
models/
*.h5
*.pkl
*.joblib

# Plots
plots/

# OS
.DS_Store
Thumbs.db
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())
    logger.info("Created .gitignore")

def main():
    """Main setup function."""
    logger.info("Starting project setup...")
    
    # Create directory structure
    create_directory_structure()
    
    # Create configuration files
    create_env_file()
    create_config_file()
    
    # Create .gitignore
    create_gitignore()
    
    logger.info("Project setup completed successfully!")

if __name__ == "__main__":
    main() 