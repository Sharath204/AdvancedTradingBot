"""
Unit tests for analysis modules.
"""

import pytest
import pandas as pd
import numpy as np
from src.analysis.support_resistance import SupportResistance
from src.analysis.signal_confidence import SignalConfidence


@pytest.fixture
def sample_ohlcv_data():
    """
    Create sample OHLCV data for testing.
    """
    dates = pd.date_range(start="2024-01-01", periods=100, freq="1h")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100) * 0.5)
    high = close + np.abs(np.random.randn(100) * 0.3)
    low = close - np.abs(np.random.randn(100) * 0.3)
    open_ = close.shift(1)
    volume = np.random.uniform(1000, 10000, 100)

    df = pd.DataFrame({
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }, index=dates)

    return df.dropna()


class TestSupportResistance:
    """
    Test support and resistance detection.
    """

    def test_find_support_resistance(self, sample_ohlcv_data):
        """
        Test support and resistance level detection.
        """
        supports, resistances = SupportResistance.find_support_resistance(
            sample_ohlcv_data
        )
        assert len(supports) > 0
        assert len(resistances) > 0
        assert supports[-1] < resistances[0]

    def test_nearest_support(self, sample_ohlcv_data):
        """
        Test nearest support calculation.
        """
        supports = [95, 98, 102]
        current = 100
        nearest = SupportResistance.get_nearest_support(current, supports)
        assert nearest == 98

    def test_nearest_resistance(self, sample_ohlcv_data):
        """
        Test nearest resistance calculation.
        """
        resistances = [95, 98, 102]
        current = 100
        nearest = SupportResistance.get_nearest_resistance(current, resistances)
        assert nearest == 102

    def test_pivot_points(self, sample_ohlcv_data):
        """
        Test pivot points calculation.
        """
        pivots = SupportResistance.calculate_pivot_points(sample_ohlcv_data)
        assert "pivot" in pivots
        assert "r1" in pivots
        assert "r2" in pivots
        assert "s1" in pivots
        assert "s2" in pivots


class TestSignalConfidence:
    """
    Test signal confidence scoring.
    """

    def test_confidence_calculation(self):
        """
        Test confidence score calculation.
        """
        analysis = {
            "trend": {"trend": "bullish", "rsi": 45, "adx": 30, "current_price": 100,
                     "ema_20": 100, "ema_50": 95, "ema_200": 90,
                     "macd": 0.5, "signal_line": 0.3, "histogram": 0.2,
                     "bb_upper": 105, "bb_middle": 100, "bb_lower": 95, "atr": 2},
            "setup": {"trend": "bullish", "rsi": 50, "adx": 25, "current_price": 100,
                     "ema_20": 100, "ema_50": 95, "ema_200": 90,
                     "macd": 0.3, "signal_line": 0.2, "histogram": 0.1,
                     "bb_upper": 105, "bb_middle": 100, "bb_lower": 95, "atr": 1.5},
            "confirmation": {"trend": "bullish", "rsi": 55, "adx": 20, "current_price": 100,
                           "ema_20": 100, "ema_50": 95, "ema_200": 90,
                           "macd": 0.2, "signal_line": 0.1, "histogram": 0.1,
                           "bb_upper": 105, "bb_middle": 100, "bb_lower": 95, "atr": 1},
        }
        result = SignalConfidence.calculate_confidence(analysis)
        assert "overall_confidence" in result
        assert "breakdown" in result
        assert 0 <= result["overall_confidence"] <= 100
