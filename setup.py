"""
Setup configuration for the package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="advanced-trading-bot",
    version="1.0.0",
    author="Sharath204",
    description="Advanced Telegram Market Analysis Bot with Technical Indicators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sharath204/AdvancedTradingBot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.11",
    install_requires=[
        "python-telegram-bot>=20.7",
        "ccxt>=4.0.58",
        "pandas>=2.2.0",
        "numpy>=1.24.3",
        "scipy>=1.13.0",
        "PyYAML>=6.0.1",
        "APScheduler>=3.10.4",
        "requests>=2.31.0",
        "aiohttp>=3.9.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.2",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "flake8>=6.1.0",
            "pylint>=3.0.3",
            "mypy>=1.7.1",
        ],
    },
)
