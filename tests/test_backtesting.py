"""
Unit tests for backtesting module.
"""

import pytest
from src.backtesting.strategy import EMACrossoverStrategy, RSIStrategy
from src.backtesting.backtest import Backtest
import pandas as pd
import numpy as np


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


class TestEMACrossoverStrategy:
    """
    Test EMA Crossover Strategy.
    """

    def test_strategy_initialization(self):
        """
        Test strategy initialization.
        """
        strategy = EMACrossoverStrategy(fast_period=20, slow_period=50)
        assert strategy.name == "EMA Crossover"
        assert strategy.fast_period == 20
        assert strategy.slow_period == 50

    def test_signal_generation(self, sample_ohlcv_data):
        """
        Test signal generation.
        """
        strategy = EMACrossoverStrategy()
        signals = strategy.generate_signals(sample_ohlcv_data)
        assert len(signals) == len(sample_ohlcv_data)
        assert signals.isin([-1, 0, 1]).all()

    def test_calculate_returns(self, sample_ohlcv_data):
        """
        Test return calculations.
        """
        strategy = EMACrossoverStrategy()
        signals = strategy.generate_signals(sample_ohlcv_data)
        performance = strategy.calculate_returns(sample_ohlcv_data, signals)
        assert "total_return" in performance
        assert "sharpe_ratio" in performance
        assert "max_drawdown" in performance
        assert "win_rate" in performance


class TestRSIStrategy:
    """
    Test RSI Strategy.
    """

    def test_strategy_initialization(self):
        """
        Test RSI strategy initialization.
        """
        strategy = RSIStrategy(period=14, oversold=30, overbought=70)
        assert strategy.name == "RSI Mean Reversion"

    def test_signal_generation(self, sample_ohlcv_data):
        """
        Test RSI signal generation.
        """
        strategy = RSIStrategy()
        signals = strategy.generate_signals(sample_ohlcv_data)
        assert len(signals) == len(sample_ohlcv_data)
        assert signals.isin([-1, 0, 1]).all()
