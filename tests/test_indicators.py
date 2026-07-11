"""
Unit tests for technical indicators.
"""

import pytest
import pandas as pd
import numpy as np
from src.indicators.moving_averages import MovingAverages
from src.indicators.momentum import Momentum
from src.indicators.volatility import Volatility
from src.indicators.volume import Volume


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


class TestMovingAverages:
    """
    Test moving averages indicators.
    """

    def test_ema_calculation(self, sample_ohlcv_data):
        """
        Test EMA calculation.
        """
        ema = MovingAverages.ema(sample_ohlcv_data["close"], 20)
        assert len(ema) == len(sample_ohlcv_data)
        assert not ema.isna().all()

    def test_sma_calculation(self, sample_ohlcv_data):
        """
        Test SMA calculation.
        """
        sma = MovingAverages.sma(sample_ohlcv_data["close"], 20)
        assert len(sma) == len(sample_ohlcv_data)
        assert sma.iloc[20:].notna().all()

    def test_trend_direction(self, sample_ohlcv_data):
        """
        Test trend direction calculation.
        """
        ema_20 = 100
        ema_50 = 95
        ema_200 = 90
        trend = MovingAverages.get_trend_direction(ema_20, ema_50, ema_200)
        assert trend == "bullish"


class TestMomentum:
    """
    Test momentum indicators.
    """

    def test_rsi_calculation(self, sample_ohlcv_data):
        """
        Test RSI calculation.
        """
        rsi = Momentum.rsi(sample_ohlcv_data["close"], 14)
        assert len(rsi) == len(sample_ohlcv_data)
        assert (rsi.dropna() >= 0).all() and (rsi.dropna() <= 100).all()

    def test_macd_calculation(self, sample_ohlcv_data):
        """
        Test MACD calculation.
        """
        macd, signal, histogram = Momentum.macd(sample_ohlcv_data["close"])
        assert len(macd) == len(sample_ohlcv_data)
        assert len(signal) == len(sample_ohlcv_data)
        assert len(histogram) == len(sample_ohlcv_data)

    def test_adx_calculation(self, sample_ohlcv_data):
        """
        Test ADX calculation.
        """
        adx = Momentum.adx(sample_ohlcv_data, 14)
        assert len(adx) == len(sample_ohlcv_data)
        assert (adx.dropna() >= 0).all()


class TestVolatility:
    """
    Test volatility indicators.
    """

    def test_atr_calculation(self, sample_ohlcv_data):
        """
        Test ATR calculation.
        """
        atr = Volatility.atr(sample_ohlcv_data, 14)
        assert len(atr) == len(sample_ohlcv_data)
        assert (atr.dropna() > 0).all()

    def test_bollinger_bands(self, sample_ohlcv_data):
        """
        Test Bollinger Bands calculation.
        """
        upper, middle, lower = Volatility.bollinger_bands(
            sample_ohlcv_data["close"], 20, 2
        )
        assert len(upper) == len(sample_ohlcv_data)
        assert (upper.dropna() > middle.dropna()).all()
        assert (lower.dropna() < middle.dropna()).all()


class TestVolume:
    """
    Test volume indicators.
    """

    def test_vwap_calculation(self, sample_ohlcv_data):
        """
        Test VWAP calculation.
        """
        vwap = Volume.vwap(sample_ohlcv_data)
        assert len(vwap) == len(sample_ohlcv_data)
        assert not vwap.isna().all()

    def test_obv_calculation(self, sample_ohlcv_data):
        """
        Test OBV calculation.
        """
        obv = Volume.on_balance_volume(sample_ohlcv_data)
        assert len(obv) == len(sample_ohlcv_data)
