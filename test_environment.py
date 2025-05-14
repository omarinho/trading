import numpy as np
import pandas as pd
import yfinance as yf
import tensorflow as tf
import torch
import vectorbt as vbt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from loguru import logger

def test_environment():
    logger.info("Testing environment setup...")
    
    # Test numpy
    arr = np.array([1, 2, 3, 4, 5])
    logger.info(f"Numpy test: {arr.mean()}")
    
    # Test pandas
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    logger.info(f"Pandas test: {df.mean()}")
    
    # Test yfinance
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d")
        logger.info(f"YFinance test: {hist.shape}")
    except Exception as e:
        logger.error(f"YFinance test failed: {e}")
    
    # Test tensorflow
    logger.info(f"TensorFlow version: {tf.__version__}")
    
    # Test PyTorch
    logger.info(f"PyTorch version: {torch.__version__}")
    
    # Test vectorbt
    logger.info(f"VectorBT version: {vbt.__version__}")
    
    # Test matplotlib
    plt.figure()
    plt.plot([1, 2, 3], [1, 2, 3])
    plt.close()
    logger.info("Matplotlib test passed")
    
    # Test seaborn
    sns.set_theme()
    logger.info("Seaborn test passed")
    
    # Test plotly
    fig = px.line(x=[1, 2, 3], y=[1, 2, 3])
    logger.info("Plotly test passed")
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    test_environment() 