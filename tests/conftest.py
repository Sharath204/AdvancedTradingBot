"""
Configuration for pytest.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_config():
    """
    Provide test configuration.
    """
    return {
        "exchange": "binance",
        "symbols": ["BTC/USDT", "ETH/USDT"],
        "timeframes": ["1m", "5m", "15m", "1h"],
    }
