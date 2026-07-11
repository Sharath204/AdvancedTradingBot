"""
Unit tests for market data module.
"""

import pytest
from src.data.market_data import MarketData
from src.utils.exceptions import MarketDataError


class TestMarketData:
    """
    Test market data module.
    """

    def test_market_data_initialization(self):
        """
        Test MarketData initialization.
        """
        market_data = MarketData(exchange_name="binance")
        assert market_data.exchange_name == "binance"
        assert market_data.exchange is not None

    def test_invalid_exchange(self):
        """
        Test invalid exchange raises error.
        """
        with pytest.raises(MarketDataError):
            MarketData(exchange_name="invalid_exchange")

    def test_cache_operations(self):
        """
        Test cache operations.
        """
        market_data = MarketData()
        market_data.data_cache["BTC/USDT_1h"] = "dummy_data"
        assert "BTC/USDT_1h" in market_data.data_cache
        market_data.clear_cache("BTC/USDT")
        assert "BTC/USDT_1h" not in market_data.data_cache
