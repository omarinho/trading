from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="trading",
    version="0.1.0",
    description="A professional-grade algorithmic trading system",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",  # We're using modern Python features
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
        ],
        "ml": [
            "tensorflow>=2.13.0",
            "torch>=2.0.1",
            "transformers>=4.31.0",
            "scikit-learn>=1.3.0",
        ],
        "backtest": [
            "backtrader>=1.9.78.123",
            "vectorbt>=0.26.0",
            "numba>=0.57.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "trading-backtest=trading.backtest.cli:main",
            "trading-fetch=trading.data.cli:main",
        ],
    },
) 